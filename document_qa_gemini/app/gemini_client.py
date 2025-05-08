import google.generativeai as genai
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Free model
        
    async def process_document_with_question(
        self, 
        file_path: str, 
        question: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Process document with Gemini and answer question"""
        try:
            # Upload file to Gemini
            file = genai.upload_file(file_path)
            
            # Prepare conversation history
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    messages.append(f"{msg['role'].capitalize()}: {msg['content']}")
            
            # Create prompt with history
            prompt = f"""You are a helpful assistant that answers questions about documents. 
            
Previous conversation:
{chr(10).join(messages) if messages else "No previous conversation."}

Current question: {question}

Please answer based on the document provided. If the answer cannot be found in the document, say so clearly."""
            
            # Generate response with file context
            response = self.model.generate_content([prompt, file])
            
            # Clean up uploaded file
            file.delete()
            
            return response.text
            
        except Exception as e:
            logging.error(f"Error in Gemini processing: {e}")
            raise Exception(f"Failed to process with Gemini: {str(e)}")
    
    async def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Get basic document analysis"""
        try:
            file = genai.upload_file(file_path)
            
            prompt = """Analyze this document and provide:
            1. A brief summary (2-3 sentences)
            2. The document type
            3. Key topics covered
            4. Approximate length/size
            
            Format as JSON."""
            
            response = self.model.generate_content([prompt, file])
            file.delete()
            
            return {"analysis": response.text}
            
        except Exception as e:
            logging.error(f"Error analyzing document: {e}")
            return {"analysis": "Unable to analyze document"}