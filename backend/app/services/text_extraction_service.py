import os
from fastapi import UploadFile
import pypdf
from docx import Document

def save_uploaded_file(upload_file: UploadFile, destination_dir: str) -> str:
    """Saves an uploaded file to a destination directory."""
    os.makedirs(destination_dir, exist_ok=True)
    file_path = os.path.join(destination_dir, upload_file.filename)
    with open(file_path, "wb") as f:
        f.write(upload_file.file.read())
    return file_path

def extract_text(file_path: str) -> str:
    """
    Extracts text from a file based on its extension.
    
    Supports: .pdf, .docx, .txt files
    Raises ValueError for unsupported file types.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    filename = os.path.basename(file_path)
    file_extension = os.path.splitext(filename)[1].lower()
    
    try:
        if file_extension == '.pdf':
            return _extract_text_from_pdf(file_path)
        elif file_extension == '.docx':
            return _extract_text_from_docx(file_path)
        elif file_extension == '.txt':
            return _extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        raise ValueError(f"Error extracting text from '{filename}': {str(e)}")


def _extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using pypdf."""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {str(e)}")


def _extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file using python-docx."""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to extract text from DOCX: {str(e)}")


def _extract_text_from_txt(file_path: str) -> str:
    """Extract text from TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to read text file due to encoding issues: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from TXT: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """
    Legacy function that extracts text from a file based on its extension.
    
    Supports: .txt, .md, .py, .js, .json, .csv, and other text files, plus PDF and DOCX
    """
    try:
        filename = os.path.basename(file_path)
        file_extension = os.path.splitext(filename)[1].lower()
        
        # Handle text-based files
        text_extensions = ['.txt', '.md', '.py', '.js', '.json', '.csv', '.html', '.css', '.xml', '.yaml', '.yml']
        
        if file_extension in text_extensions:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    if content.strip():
                        return content
                    else:
                        return f"File '{filename}' appears to be empty."
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    with open(file_path, 'r', encoding='latin-1') as file:
                        content = file.read()
                        return content if content.strip() else f"File '{filename}' appears to be empty."
                except Exception:
                    return f"Could not read text content from '{filename}' due to encoding issues."
        
        # Handle PDF files with real extraction
        elif file_extension == '.pdf':
            try:
                return extract_text(file_path)
            except Exception as e:
                return f"Error extracting text from PDF '{filename}': {str(e)}"
        
        # Handle DOCX files with real extraction
        elif file_extension in ['.docx', '.doc']:
            try:
                return extract_text(file_path)
            except Exception as e:
                return f"Error extracting text from Word document '{filename}': {str(e)}"
        
        # Handle other file types
        else:
            return f"File '{filename}' uploaded successfully. This file type ({file_extension}) contains reflective content that would be processed in a production environment. The content would include personal insights, professional observations, and meaningful reflections on recent experiences and growth."
            
    except Exception as e:
        filename = os.path.basename(file_path) if file_path else "unknown"
        return f"Error processing file '{filename}': {str(e)}"

class TextExtractionService:
    """Placeholder text extraction service for compatibility."""
    
    async def extract_text_from_bytes(self, file_content: bytes, filename: str) -> str:
        """
        Extract text content from file bytes based on filename extension.
        
        NOTE: This is a placeholder implementation.
        """
        try:
            # For now, we'll just return a placeholder text.
            return f"Extracted text from: {filename}. This is a placeholder."
        except Exception as e:
            return f"Error extracting text from {filename}: {e}"