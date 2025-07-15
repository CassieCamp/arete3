from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import List
import logging
from datetime import datetime

from app.api.v1.deps import get_current_user
from app.models.journey.reflection import ReflectionSource
from app.models.journey.enums import DocumentType, ProcessingStatus
from app.repositories.journey.reflection_repository import ReflectionSourceRepository
from app.repositories.journey.insight_repository import InsightRepository
from app.services.journey.file_storage_service import FileStorageService
from app.services.text_extraction_service import extract_text_from_file
from app.services.journey.ai_processor import analyze_text_for_insights
from app.schemas.journey import JourneyFeedResponse, JourneyFeedItem
from app.db.mongodb import get_database

logger = logging.getLogger(__name__)
router = APIRouter()

def get_reflection_repository() -> ReflectionSourceRepository:
    """Dependency to get reflection repository with database connection."""
    return ReflectionSourceRepository()

@router.get("/", response_model=List[ReflectionSource])
async def get_reflection_sources(
    user_info: dict = Depends(get_current_user),
    reflection_repo: ReflectionSourceRepository = Depends(get_reflection_repository)
):
    """
    Get all reflection documents for the currently authenticated user.
    
    Returns:
        List[ReflectionSource]: List of all reflection documents for the user.
                               Returns empty list if no documents are found.
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"Getting reflection sources for user: {user_id}")
        
        # Get all reflection documents for the user
        reflections = await reflection_repo.get_by_user_id(user_id)
        
        logger.info(f"Successfully retrieved {len(reflections)} reflection sources for user: {user_id}")
        return reflections
        
    except Exception as e:
        logger.error(f"Error retrieving reflection sources for user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving reflection sources"
        )

@router.post("/upload", response_model=ReflectionSource)
async def upload_reflection_document(
    file: UploadFile = File(...),
    user_info: dict = Depends(get_current_user),
    reflection_repo: ReflectionSourceRepository = Depends(get_reflection_repository)
):
    """
    Upload a document, save it, extract text, and create a reflection source.
    Complete end-to-end implementation with proper error handling.
    """
    user_id = user_info['clerk_user_id']
    logger.info(f"Starting document upload for user: {user_id}, file: {file.filename}")
    
    # Initialize services
    file_storage_service = FileStorageService()
    
    try:
        # 1. Save file using the proper method
        file_path = file_storage_service.save_reflection_document(user_id, file)
        logger.info(f"File saved successfully to: {file_path}")
        
        # 2. Extract text content
        text_content = extract_text_from_file(file_path)
        logger.info(f"Text extraction completed, content length: {len(text_content) if text_content else 0}")
        
        # 3. Calculate word count
        word_count = len(text_content.split()) if text_content else 0
        character_count = len(text_content) if text_content else 0
        
        # 4. Determine document type based on content type
        document_type = DocumentType.PDF
        if file.content_type:
            if "pdf" in file.content_type.lower():
                document_type = DocumentType.PDF
            elif "word" in file.content_type.lower() or "docx" in file.content_type.lower():
                document_type = DocumentType.DOCX
            else:
                document_type = DocumentType.TEXT
        
        # 5. Perform AI analysis on the extracted text
        document_analysis = None
        processing_status = ProcessingStatus.PROCESSING
        ai_processing_completed_at = None
        
        try:
            if text_content and text_content.strip():
                logger.info("Starting AI analysis of extracted text")
                document_analysis = await analyze_text_for_insights(text_content)
                processing_status = ProcessingStatus.COMPLETED
                ai_processing_completed_at = datetime.utcnow()
                logger.info("✅ AI analysis completed successfully")
            else:
                logger.warning("No text content available for AI analysis")
                processing_status = ProcessingStatus.COMPLETED  # Still mark as completed if no text to analyze
        except Exception as ai_error:
            logger.error(f"❌ AI analysis failed: {ai_error}")
            processing_status = ProcessingStatus.FAILED
            # Continue with document creation even if AI fails
        
        # 6. Create ReflectionSource record with complete data including AI analysis
        reflection = ReflectionSource(
            user_id=user_id,
            title=file.filename or "Untitled Document",
            content=text_content,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            content_type=file.content_type,
            document_type=document_type,
            document_analysis=document_analysis,  # Include AI analysis results
            word_count=word_count,
            character_count=character_count,
            processing_status=processing_status,
            text_extraction_completed_at=datetime.utcnow(),
            ai_processing_completed_at=ai_processing_completed_at,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 7. Save to database
        created_reflection = await reflection_repo.create(reflection)
        logger.info(f"Reflection created successfully with ID: {created_reflection.id}")
        
        return created_reflection
        
    except HTTPException:
        # Re-raise HTTP exceptions from file storage service
        raise
    except Exception as e:
        logger.error(f"Upload failed for user {user_id}, file {file.filename}: {e}")
        
        # Try to create a failed record if we have basic info
        try:
            failed_reflection = ReflectionSource(
                user_id=user_id,
                title=file.filename or "Failed Upload",
                content=f"Processing failed: {str(e)}",
                original_filename=file.filename,
                file_size=file.size,
                content_type=file.content_type,
                processing_status=ProcessingStatus.FAILED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            await reflection_repo.create(failed_reflection)
        except Exception as db_error:
            logger.error(f"Failed to create failed record: {db_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document upload: {str(e)}"
        )

@router.get("/insights", response_model=dict)
async def get_insights(
    user_info: dict = Depends(get_current_user),
    reflection_repo: ReflectionSourceRepository = Depends(get_reflection_repository)
):
    """
    Get real insights data from the database for the user's journey feed.
    
    This endpoint returns actual ReflectionSource documents from the database
    instead of mock data, providing real user reflections and insights.
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"=== get_insights called ===")
        logger.info(f"user: {user_id}")
        
        # Fetch all ReflectionSource documents for the user from the database
        reflections = await reflection_repo.get_by_user_id(user_id)
        
        # Convert ReflectionSource objects to the format expected by frontend
        insights = []
        for reflection in reflections:
            insight_data = {
                "id": str(reflection.id),
                "title": reflection.title,
                "summary": reflection.content[:150] + "..." if reflection.content and len(reflection.content) > 150 else reflection.content or "",
                "content": reflection.content,
                "categories": reflection.categories if reflection.categories else ["general"],
                "tags": reflection.tags if reflection.tags else [],
                "key_points": [reflection.content[:200]] if reflection.content else [],
                "action_items": [],
                "processing_status": reflection.processing_status.value if reflection.processing_status else "completed",
                "word_count": reflection.word_count,
                "document_type": reflection.document_type.value if reflection.document_type else None,
                "original_filename": reflection.original_filename,
                "created_at": reflection.created_at.isoformat() if reflection.created_at else "",
                "updated_at": reflection.updated_at.isoformat() if reflection.updated_at else ""
            }
            insights.append(insight_data)
        
        response = {
            "data": {
                "insights": insights,
                "reflections": insights  # Also provide as reflections for compatibility
            }
        }
        
        logger.info(f"✅ Successfully retrieved {len(insights)} real insights from database")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in get_insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving insights"
        )
    

@router.get("/journey/feed", response_model=JourneyFeedResponse)
async def get_journey_feed(
    user_info: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get the journey feed with real reflections and insights for the user.
    """
    user_id = user_info['clerk_user_id']
    reflection_repo = ReflectionSourceRepository()
    insight_repo = InsightRepository()

    reflections = await reflection_repo.get_all_for_user(user_id, skip=skip, limit=limit)
    
    feed_items = []
    for r in reflections:
        feed_items.append(JourneyFeedItem(
            type="reflection",
            id=r.id,
            title=r.title,
            content=r.content,
            summary=r.content[:150] + "..." if r.content else "",
            created_at=r.created_at,
            # Add other relevant fields from your JourneyFeedItem schema
        ))

    # In the future, you would also fetch and interleave insights.
    
    return JourneyFeedResponse(
        items=feed_items,
        total_count=len(feed_items), # This should be a proper count query in a real app
        skip=skip,
        limit=limit,
        category_counts={} # Placeholder
    )