from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from pathlib import Path
import re

def load_document(file_path:str):
    extension = Path(file_path).suffix.lower()
    if extension == '.pdf':
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
    elif extension == '.docx':
        loader = Docx2txtLoader(file_path)
        docs = loader.load()

    else:
        return 'Unsupported file type'

    pages = len(docs)

    text = "\n".join(
    doc.page_content for doc in docs)

    return pages, text
    

def cleaning(text: str):
    text = text.replace('\r\n', '\n').replace('\r', '\n')   # normalize line endings
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)          # fix hyphenated line breaks
    text = re.sub(r'\n{3,}', '\n\n', text)                   # max 2 consecutive newlines
    text = re.sub(r"[•●▪️▫️◦○◉◎◆◇♦️◈■□►▸▹▶▷➤➜➔→←↑↓✓✔☑✗✘★☆※❖❯❮]", "-", text)  # bullets
    text = re.sub(r'\t+', ' ', text)                         # tabs to space
    text = re.sub(r'[^\x20-\x7E\n]', '', text)              # remove non-printable (^ fixed)
    text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())  # trim each line
    return text.strip()


