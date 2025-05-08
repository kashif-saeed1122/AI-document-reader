from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any
import logging
import os
from datetime import datetime

from .models import (
    DocumentSession, 
    QuestionRequest, 
    QuestionResponse, 
    UploadResponse, 
    DocumentMetadata
)
from .gemini_client import GeminiClient
from .document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Document Q&A with Gemini")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
gemini_client = GeminiClient()
doc_processor = DocumentProcessor()

# In-memory session storage (replace with Redis in production)
sessions: Dict[str, DocumentSession] = {}

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for Q&A"""
    try:
        # Validate file type
        if not doc_processor.validate_file_type(file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Allowed: PDF, DOCX, TXT, MD"
            )
        
        # Process and save file
        file_path, metadata = await doc_processor.save_and_process_file(file)
        
        # Create session
        session = DocumentSession(
            session_id=metadata["session_id"],
            metadata=DocumentMetadata(**metadata),
            file_path=file_path
        )
        
        # Store session
        sessions[session.session_id] = session
        
        return UploadResponse(
            session_id=session.session_id,
            message="Document uploaded successfully",
            metadata=session.metadata
        )
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the uploaded document"""
    try:
        # Get session
        session = sessions.get(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Process question with Gemini
        answer = await gemini_client.process_document_with_question(
            file_path=session.file_path,
            question=request.question,
            conversation_history=session.conversation_history
        )
        
        # Update conversation history
        session.conversation_history.append({"role": "user", "content": request.question})
        session.conversation_history.append({"role": "assistant", "content": answer})
        
        return QuestionResponse(
            answer=answer,
            session_id=request.session_id
        )
        
    except Exception as e:
        logging.error(f"Question processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "metadata": session.metadata,
        "conversation_history": session.conversation_history
    }

# MCP-compatible endpoints
@app.post("/mcp/v1/completion")
async def mcp_completion(request: Dict[str, Any]):
    """MCP-compatible completion endpoint"""
    try:
        # Extract parameters
        prompt = request.get("prompt", "")
        session_id = request.get("session_id")
        
        if session_id and session_id in sessions:
            session = sessions[session_id]
            answer = await gemini_client.process_document_with_question(
                file_path=session.file_path,
                question=prompt,
                conversation_history=session.conversation_history
            )
        else:
            answer = "No document context available. Please upload a document first."
        
        return {
            "completion": answer,
            "model": "gemini-1.5-flash",
            "session_id": session_id
        }
        
    except Exception as e:
        logging.error(f"MCP completion error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)