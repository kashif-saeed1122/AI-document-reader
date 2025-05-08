import PyPDF2
import docx
import io
import logging
import re

def process_document(file_content, filename):
    """Extract text from different document types - NO SIZE LIMITS"""
    file_extension = filename.lower().split('.')[-1]
    
    try:
        if file_extension == 'pdf':
            return extract_text_from_pdf(file_content)
        elif file_extension == 'docx':
            return extract_text_from_docx(file_content)
        elif file_extension == 'txt':
            return file_content.decode('utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise

def extract_text_from_pdf(pdf_content):
    """Extract text from PDF - handles large PDFs"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text = []
        total_pages = len(pdf_reader.pages)
        
        logging.info(f"Processing PDF with {total_pages} pages")
        
        for i, page in enumerate(pdf_reader.pages):
            if i % 10 == 0:  # Log progress every 10 pages
                logging.info(f"Processing page {i+1}/{total_pages}")
            text.append(page.extract_text())
        
        return "\n\n".join(text)
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise

def extract_text_from_docx(docx_content):
    """Extract text from DOCX - handles large documents"""
    try:
        doc = docx.Document(io.BytesIO(docx_content))
        text = []
        
        for i, paragraph in enumerate(doc.paragraphs):
            if i % 100 == 0:  # Log progress every 100 paragraphs
                logging.info(f"Processing paragraph {i}")
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return "\n\n".join(text)
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        raise

def optimize_for_large_context(text, max_chars=1200000):
    """
    Optimize text for 300k token context (roughly 1.2M characters)
    This function just ensures we don't exceed the context window
    """
    if len(text) <= max_chars:
        return text
    
    logging.info(f"Text too large ({len(text)} chars), optimizing for context window")
    
    # If text is too large, we'll take the most important parts
    # For now, just truncate - you could implement smarter selection here
    return text[:max_chars]

def estimate_tokens(text):
    """Rough estimation of tokens (about 4 characters per token)"""
    return len(text) / 4