from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from app.api.v1.deps import get_current_user_clerk_id
from app.services.document_service import DocumentService
from app.services.user_service import UserService
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse
from app.models.document import DocumentCategory, DocumentType
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get all documents for the currently authenticated user.
    
    Args:
        clerk_user_id: Clerk user ID from authentication
    
    Returns:
        List[DocumentResponse]: List of user's documents
    """
    try:
        logger.info(f"=== Get user documents endpoint called ===")
        logger.info(f"clerk_user_id: {clerk_user_id}")
        
        # Get user_id from user service using clerk_user_id
        user_service = UserService()
        user = await user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        user_id = str(user.id)
        logger.info(f"Found user_id: {user_id}")
        
        # Initialize document service
        document_repository = DocumentRepository()
        document_service = DocumentService(document_repository)
        
        # Get all documents for the user
        documents = await document_service.get_user_documents(user_id)
        
        logger.info(f"✅ Retrieved {len(documents)} documents for user")
        
        # Convert to response format
        document_responses = []
        for doc in documents:
            document_responses.append(DocumentResponse(
                id=str(doc.id),
                user_id=doc.user_id,
                clerk_user_id=doc.clerk_user_id,
                file_name=doc.file_name,
                file_type=doc.file_type,
                file_size=doc.file_size,
                s3_url=doc.s3_url,
                local_path=doc.local_path,
                extracted_text=doc.extracted_text,
                category=doc.category,
                tags=doc.tags,
                description=doc.description,
                is_processed=doc.is_processed,
                processing_error=doc.processing_error,
                created_at=doc.created_at,
                updated_at=doc.updated_at
            ))
        
        return document_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving documents: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
    description: Optional[str] = Form(None),
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Upload a document with multipart/form-data.
    
    Args:
        file: The uploaded file
        category: Document category (must be a valid DocumentCategory)
        description: Optional description of the document
        clerk_user_id: Clerk user ID from authentication
    
    Returns:
        DocumentResponse: The newly created document object
    """
    try:
        logger.info(f"=== Document upload endpoint called ===")
        logger.info(f"clerk_user_id: {clerk_user_id}")
        logger.info(f"file: {file.filename}, category: {category}")
        
        # Get user_id from user service using clerk_user_id
        user_service = UserService()
        user = await user_service.get_user_by_clerk_id(clerk_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        user_id = str(user.id)
        logger.info(f"Found user_id: {user_id}")
        
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        # Extract file extension
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        # Validate file type against supported types
        try:
            document_type = DocumentType(file_extension)
        except ValueError:
            supported_types = [t.value for t in DocumentType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}. Supported types: {supported_types}"
            )
        
        # Validate category
        try:
            document_category = DocumentCategory(category.lower())
        except ValueError:
            supported_categories = [c.value for c in DocumentCategory]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}. Supported categories: {supported_categories}"
            )
        
        # Initialize document service
        document_repository = DocumentRepository()
        document_service = DocumentService(document_repository)
        
        # Upload the document
        uploaded_document = await document_service.upload_document(
            user_id=user_id,
            clerk_user_id=clerk_user_id,
            file=file.file,
            file_name=file.filename,
            file_type=file_extension,
            category=category
        )
        
        logger.info(f"✅ Document uploaded successfully with ID: {uploaded_document.id}")
        
        # Return the document response
        return DocumentResponse(
            id=str(uploaded_document.id),
            user_id=uploaded_document.user_id,
            clerk_user_id=uploaded_document.clerk_user_id,
            file_name=uploaded_document.file_name,
            file_type=uploaded_document.file_type,
            file_size=uploaded_document.file_size,
            s3_url=uploaded_document.s3_url,
            local_path=uploaded_document.local_path,
            extracted_text=uploaded_document.extracted_text,
            category=uploaded_document.category,
            tags=uploaded_document.tags,
            description=uploaded_document.description,
            is_processed=uploaded_document.is_processed,
            processing_error=uploaded_document.processing_error,
            created_at=uploaded_document.created_at,
            updated_at=uploaded_document.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error uploading document: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )