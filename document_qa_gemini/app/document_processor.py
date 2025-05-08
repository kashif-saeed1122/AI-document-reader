import os
import uuid
import logging
from typing import Dict, Tuple
import PyPDF2
import docx
from fastapi import UploadFile
import aiofiles
from datetime import datetime

class DocumentProcessor:
    def __init__(self):
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
        
    async def save_and_process_file(self, file: UploadFile) -> Tuple[str, Dict]:
        """Save uploaded file and extract metadata"""
        try:
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Create session directory
            session_dir = os.path.join(self.upload_dir, session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(session_dir, file.filename)
            
            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Extract file metadata
            file_type = file.filename.split('.')[-1].lower()
            file_size = len(content)
            
            metadata = {
                "filename": file.filename,
                "file_type": file_type,
                "file_size": file_size,
                "upload_time": datetime.now(),
                "session_id": session_id
            }
            
            return file_path, metadata
            
        except Exception as e:
            logging.error(f"Error processing file: {e}")
            raise Exception(f"Failed to process file: {str(e)}")
    
    def validate_file_type(self, filename: str) -> bool:
        """Validate if file type is supported"""
        allowed_extensions = ['pdf', 'docx', 'txt', 'md']
        file_ext = filename.split('.')[-1].lower()
        return file_ext in allowed_extensions