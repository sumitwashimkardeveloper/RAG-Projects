import PyPDF2
from docx import Document
import os
from typing import List, Tuple
import hashlib

class DocumentLoader:
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 256):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_pdf(self, file_path: str) -> List[str]:
        texts = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    texts.append(text)
        return texts

    def load_docx(self, file_path: str) -> List[str]:
        doc = Document(file_path)
        texts = []
        for para in doc.paragraphs:
            if para.text:
                texts.append(para.text)
        return texts

    def load_txt(self, file_path: str) -> List[str]:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return [text]

    def load_document(self, file_path: str) -> Tuple[List[str], str]:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext == '.pdf':
            texts = self.load_pdf(file_path)
        elif ext == '.docx':
            texts = self.load_docx(file_path)
        elif ext == '.txt':
            texts = self.load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        combined_text = ' '.join(texts)
        doc_id = hashlib.md5(combined_text.encode()).hexdigest()[:12]

        return texts, doc_id

    def chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)

            start = end - self.chunk_overlap

        return [c for c in chunks if len(c.strip()) > 50]

    def load_and_chunk_document(self, file_path: str) -> Tuple[List[str], str]:
        texts, doc_id = self.load_document(file_path)
        combined_text = ' '.join(texts)
        chunks = self.chunk_text(combined_text)
        return chunks, doc_id

    def load_directory(self, directory_path: str) -> List[Tuple[List[str], str]]:
        results = []
        supported_extensions = {'.pdf', '.docx', '.txt'}

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in supported_extensions:
                    try:
                        chunks, doc_id = self.load_and_chunk_document(file_path)
                        results.append((chunks, doc_id))
                    except Exception as e:
                        print(f"Error loading {filename}: {str(e)}")

        return results

document_loader = DocumentLoader()
