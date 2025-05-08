from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    file_size: int
    upload_time: datetime = datetime.now()
    session_id: str

class DocumentSession(BaseModel):
    session_id: str
    metadata: DocumentMetadata
    file_path: Optional[str] = None
    conversation_history: List[Dict[str, str]] = []

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = datetime.now()

class QuestionRequest(BaseModel):
    session_id: str
    question: str

class QuestionResponse(BaseModel):
    answer: str
    session_id: str

class UploadResponse(BaseModel):
    session_id: str
    message: str
    metadata: DocumentMetadata