## install virtual environemnt

`python -m venv .venv`

## activate the virtual env

`.venv\Scripts\activate`

## install the requirements file

`pip install -r document_qa_gemini/requirements.txt`

## navigate to document_qa_gemini folder

`cd document_qa_gemini folder`

## run the server

uvicorn app.main:app --relaod
