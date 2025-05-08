from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging
from utils import process_document, optimize_for_large_context

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
# REMOVED FILE SIZE LIMIT - NO LIMITS!

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Store document content in memory
document_storage = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Read file content - NO SIZE LIMITS
        file_content = file.read()
        filename = secure_filename(file.filename)
        
        logging.info(f"Processing file: {filename}, Size: {len(file_content)} bytes")
        
        # Process document
        document_text = process_document(file_content, filename)
        
        # Optimize for 300k token context
        optimized_text = optimize_for_large_context(document_text)
        
        # Generate a simple session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Store in memory
        document_storage[session_id] = {
            'filename': filename,
            'full_text': optimized_text,
            'original_size': len(file_content),
            'text_size': len(optimized_text)
        }
        
        return jsonify({
            'message': 'File uploaded successfully',
            'session_id': session_id,
            'file_size': len(file_content),
            'text_size': len(optimized_text)
        })
        
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    session_id = data.get('session_id')
    question = data.get('question')
    
    if not session_id or session_id not in document_storage:
        return jsonify({'error': 'Invalid session'}), 400
    
    if not question:
        return jsonify({'error': 'No question provided'}), 400
    
    try:
        document_data = document_storage[session_id]
        
        # Create messages for OpenAI - using full document
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions about documents. 
                Use the provided document content to answer questions accurately. 
                If the answer cannot be found in the document, say so clearly.
                The document might be very large, so be thorough in your search."""
            },
            {
                "role": "user",
                "content": f"Document content:\n\n{document_data['full_text']}\n\nQuestion: {question}"
            }
        ]
        
        # Get response from OpenAI using gpt-4.1-nano with 300k context
        response = client.chat.completions.create(
            model="gpt-4.1-nano",  # Using the 300k context model
            messages=messages,
            temperature=0.3,
            max_tokens=4000  # Increased for longer answers
        )
        
        answer = response.choices[0].message.content
        
        return jsonify({'answer': answer})
        
    except Exception as e:
        logging.error(f"Question error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)