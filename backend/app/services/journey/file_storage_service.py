import os
import uuid
from fastapi import UploadFile, HTTPException
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FileStorageService:
    """Service for storing uploaded files."""
    def __init__(self, base_directory: str = "uploads"):
        self.base_directory = base_directory

    def save_file(self, user_id: str, file: UploadFile) -> str:
        """Saves a file to a user-specific directory and returns the path."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        
        # Sanitize filename
        sanitized_filename = "".join(c for c in os.path.basename(file.filename) if c.isalnum() or c in ('.', '_')).rstrip()
        
        # Create a unique filename
        unique_filename = f"{timestamp}_{unique_id}_{sanitized_filename}"
        
        # Create user-specific directory
        user_directory = os.path.join(self.base_directory, "reflections", user_id)
        os.makedirs(user_directory, exist_ok=True)
        
        file_path = os.path.join(user_directory, unique_filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
            
        return file_path

    def save_reflection_document(self, user_id: str, file: UploadFile) -> str:
        """
        Saves a reflection document to a user-specific directory.
        
        Args:
            user_id: The ID of the user uploading the file
            file: The uploaded file object
            
        Returns:
            str: The absolute file path of the saved file
            
        Raises:
            HTTPException: If file operations fail
        """
        try:
            # Validate input parameters
            if not user_id or not user_id.strip():
                raise HTTPException(status_code=400, detail="User ID is required")
            
            if not file or not file.filename:
                raise HTTPException(status_code=400, detail="Valid file is required")
            
            # Construct user-specific directory path
            user_directory = os.path.join(self.base_directory, "reflections", user_id)
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(user_directory, exist_ok=True)
            except OSError as e:
                logger.error(f"Failed to create directory {user_directory}: {e}")
                raise HTTPException(status_code=500, detail="Failed to create storage directory")
            
            # Preserve original filename but sanitize it for security
            original_filename = os.path.basename(file.filename)
            sanitized_filename = "".join(c for c in original_filename if c.isalnum() or c in ('.', '_', '-', ' ')).rstrip()
            
            if not sanitized_filename:
                raise HTTPException(status_code=400, detail="Invalid filename")
            
            # Construct full file path
            file_path = os.path.join(user_directory, sanitized_filename)
            
            # Handle file name conflicts by appending a number
            counter = 1
            base_name, extension = os.path.splitext(sanitized_filename)
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{extension}"
                file_path = os.path.join(user_directory, new_filename)
                counter += 1
            
            # Save the file
            try:
                with open(file_path, "wb") as buffer:
                    # Reset file pointer to beginning
                    file.file.seek(0)
                    content = file.file.read()
                    if not content:
                        raise HTTPException(status_code=400, detail="File is empty")
                    buffer.write(content)
                    
            except OSError as e:
                logger.error(f"Failed to write file {file_path}: {e}")
                raise HTTPException(status_code=500, detail="Failed to save file")
            except Exception as e:
                logger.error(f"Unexpected error saving file {file_path}: {e}")
                raise HTTPException(status_code=500, detail="Failed to save file")
            
            # Return absolute path
            absolute_path = os.path.abspath(file_path)
            logger.info(f"Successfully saved reflection document to {absolute_path}")
            return absolute_path
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in save_reflection_document: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")