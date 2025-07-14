import os
from typing import BinaryIO, List
from app.models.document import Document, DocumentType, DocumentCategory
from app.repositories.document_repository import DocumentRepository
from app.services.text_extraction_service import TextExtractionService
from app.services.session_insight_service import SessionInsightService
import logging

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, document_repository: DocumentRepository, session_insight_service: SessionInsightService):
        self.document_repository = document_repository
        self.text_extraction_service = TextExtractionService()
        self.session_insight_service = session_insight_service

    async def upload_document(
        self,
        user_id: str,
        clerk_user_id: str,
        file: BinaryIO,
        file_name: str,
        file_type: str,
        category: str
    ) -> Document:
        """
        Upload a document and save its metadata to the database.
        
        Args:
            user_id: The MongoDB ObjectId of the user uploading the document
            clerk_user_id: The Clerk user ID for direct integration
            file: The file object to be uploaded
            file_name: The name of the file
            file_type: The file extension/type (must be a valid DocumentType)
            category: The category/type of the document (must be a valid DocumentCategory)
            
        Returns:
            Document: The newly created document object
        """
        logger.info(f"=== DocumentService.upload_document called ===")
        logger.info(f"user_id: {user_id}, clerk_user_id: {clerk_user_id}, file_name: {file_name}")
        
        try:
            # Create uploads directory if it doesn't exist
            uploads_dir = "uploads"
            os.makedirs(uploads_dir, exist_ok=True)
            logger.info(f"Ensured uploads directory exists: {uploads_dir}")
            
            # Generate a unique file path
            # In a real application, you might want to add timestamp or UUID to avoid conflicts
            file_path = os.path.join(uploads_dir, file_name)
            logger.info(f"File will be saved to: {file_path}")
            
            # Save file to local directory (placeholder for S3 upload)
            # TODO: Replace this with S3 upload logic in production
            with open(file_path, "wb") as f:
                # Read file content and write to local storage
                file_content = file.read()
                f.write(file_content)
            
            file_size = len(file_content)
            logger.info(f"File saved successfully, size: {file_size} bytes")
            
            # Validate and convert file_type to DocumentType enum
            try:
                document_type = DocumentType(file_type.lower())
            except ValueError:
                logger.error(f"Invalid file type: {file_type}")
                raise ValueError(f"Unsupported file type: {file_type}. Supported types: {[t.value for t in DocumentType]}")
            
            # Validate and convert category to DocumentCategory enum
            try:
                document_category = DocumentCategory(category.lower())
            except ValueError:
                logger.error(f"Invalid category: {category}")
                raise ValueError(f"Invalid category: {category}. Supported categories: {[c.value for c in DocumentCategory]}")
            
            # Create new Document object
            document = Document(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                file_name=file_name,
                file_type=document_type,
                file_size=file_size,
                local_path=file_path,
                category=document_category,
                is_processed=False  # Will be set to True after text extraction
            )
            
            logger.info(f"Created document object: {document}")
            
            # Save document metadata to database using repository
            saved_document = await self.document_repository.create_document(document)
            
            logger.info(f"Document saved with ID: {saved_document.id}, now extracting text...")
            
            # Extract text from the uploaded document
            await self._extract_and_update_document_text(saved_document, file_path, file_type)
            
            logger.info(f"✅ Successfully uploaded and processed document with ID: {saved_document.id}")
            return saved_document
            
        except Exception as e:
            logger.error(f"❌ Error in upload_document: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Clean up the file if it was created but database save failed
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up file: {file_path}")
                except Exception as cleanup_error:
                    logger.error(f"Failed to clean up file {file_path}: {cleanup_error}")
            
            raise

    async def get_user_documents(self, user_id: str) -> List[Document]:
        """
        Get all documents for a specific user.
        
        Args:
            user_id: The MongoDB ObjectId of the user
            
        Returns:
            List[Document]: List of user's documents
        """
        logger.info(f"=== DocumentService.get_user_documents called ===")
        logger.info(f"user_id: {user_id}")
        
        try:
            documents = await self.document_repository.get_documents_by_user_id(user_id)
            logger.info(f"✅ Retrieved {len(documents)} documents for user {user_id}")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error in get_user_documents: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def _extract_and_update_document_text(self, document: Document, file_path: str, file_type: str) -> None:
        """
        Extract text from a document and update the database record.
        
        Args:
            document: The document object to update
            file_path: Path to the file to extract text from
            file_type: Type of the file (pdf, docx, txt, etc.)
        """
        logger.info(f"=== DocumentService._extract_and_update_document_text called ===")
        logger.info(f"Processing document ID: {document.id}, file_path: {file_path}, file_type: {file_type}")
        
        try:
            # Check if the file type is supported for text extraction
            if not self.text_extraction_service.is_supported_file_type(file_type):
                logger.warning(f"File type '{file_type}' is not supported for text extraction")
                # Update document with processing error
                await self.document_repository.update_document(
                    str(document.id),
                    {
                        "is_processed": True,
                        "processing_error": f"File type '{file_type}' is not supported for text extraction"
                    }
                )
                return
            
            # Extract text from the document
            extracted_text = self.text_extraction_service.extract_text_from_file(file_path, file_type)
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters of text")
            
            # Update the document in the database with extracted text
            update_data = {
                "extracted_text": extracted_text,
                "is_processed": True,
                "processing_error": None  # Clear any previous errors
            }
            
            updated_document = await self.document_repository.update_document(
                str(document.id),
                update_data
            )
            
            if updated_document:
                logger.info(f"✅ Successfully updated document {document.id} with extracted text")
                
                # Generate AI-powered metadata and insight from the extracted text
                try:
                    logger.info(f"🧠 Generating AI metadata and insight for document {document.id}")
                    
                    # Generate intelligent title and metadata using AI
                    from app.services.ai_service import AIService
                    ai_service = AIService()
                    
                    metadata = await ai_service.generate_document_metadata(
                        filename=document.file_name,
                        content=extracted_text
                    )
                    
                    logger.info(f"✅ Generated AI metadata: {metadata.get('title', 'No title')}")
                    
                    # Update document with AI-generated metadata
                    await self.document_repository.update_document(
                        str(document.id),
                        {
                            "description": metadata.get("description", ""),
                            "tags": metadata.get("tags", []),
                            "category": metadata.get("category", document.category.value)
                        }
                    )
                    
                    # Create insight with AI-generated title
                    ai_title = metadata.get("title", document.file_name)
                    await self.session_insight_service.create_unpaired_insight_from_transcript(
                        client_user_id=document.clerk_user_id,
                        transcript_content=extracted_text,
                        session_title=ai_title,
                        source_document_id=str(document.id)
                    )
                    logger.info(f"✅ Successfully generated insight for document {document.id} with AI title: {ai_title}")
                    
                except Exception as insight_error:
                    logger.error(f"❌ Error generating AI metadata/insight for document {document.id}: {insight_error}")
                    # Fallback to original behavior
                    try:
                        await self.session_insight_service.create_unpaired_insight_from_transcript(
                            client_user_id=document.clerk_user_id,
                            transcript_content=extracted_text,
                            session_title=document.file_name,
                            source_document_id=str(document.id)
                        )
                        logger.info(f"✅ Fallback: Generated insight with original filename")
                    except Exception as fallback_error:
                        logger.error(f"❌ Fallback insight generation also failed: {fallback_error}")
                    # Don't raise the error as the document was successfully processed
            else:
                logger.error(f"Failed to update document {document.id} in database")
                
        except Exception as e:
            logger.error(f"❌ Error extracting text from document {document.id}: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Update document with processing error
            try:
                await self.document_repository.update_document(
                    str(document.id),
                    {
                        "is_processed": True,
                        "processing_error": f"Text extraction failed: {str(e)}"
                    }
                )
                logger.info(f"Updated document {document.id} with processing error")
            except Exception as update_error:
                logger.error(f"Failed to update document with error status: {update_error}")