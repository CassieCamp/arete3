"""
Reflections API Endpoints

This module contains API endpoints for managing reflection sources in the Journey System.
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks, Query
from typing import Optional, List
import logging

from app.api.v1.deps import get_current_user
from app.repositories.journey.reflection_repository import ReflectionRepository
from app.repositories.journey.insight_repository import InsightRepository
from app.services.text_extraction_service import save_uploaded_file, extract_text_from_file
from app.services.journey.insight_template_engine import InsightTemplateEngine
from app.models.journey.reflection import ReflectionSource
from app.models.journey.insight import Insight
from app.models.journey.enums import ProcessingStatus, DocumentType, CategoryType, ReviewStatus
from app.schemas.journey import ReflectionResponse, InsightResponse, JourneyFeedResponse, JourneyFeedItem

logger = logging.getLogger(__name__)
router = APIRouter()


def process_reflection_ai(reflection_id: str, user_id: str):
    """
    Background task placeholder for AI processing of reflections.
    This will be implemented in the reflection AI service.
    """
    logger.info(f"Starting AI processing for reflection {reflection_id} (user: {user_id})")
    # TODO: Implement actual AI processing
    pass


@router.post("/upload", response_model=ReflectionResponse)
async def upload_reflection_document(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="Title for the reflection"),
    description: Optional[str] = Form(None, description="Optional description"),
    file: UploadFile = File(..., description="Document file to upload"),
    user_info: dict = Depends(get_current_user)
):
    """
    Upload a document file and create a reflection source.
    
    This endpoint:
    1. Validates the uploaded file (PDF, DOCX, TXT)
    2. Saves the file to the uploads directory
    3. Extracts text content from the file
    4. Creates a ReflectionSource record in the database
    5. Queues the reflection for AI processing
    
    Supported file types: PDF, DOCX, TXT
    Maximum file size: 10MB
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"=== upload_reflection_document called ===")
        logger.info(f"user: {user_id}, title: {title}, file: {file.filename}")
        
        # Validate file type
        allowed_content_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "text/plain"
        ]
        
        if file.content_type not in allowed_content_types:
            logger.warning(f"Unsupported file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, DOCX, TXT"
            )
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB"
            )
        
        # Reset file position for saving
        await file.seek(0)
        
        # Save the uploaded file
        try:
            file_path = await save_uploaded_file(file)
            logger.info(f"File saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded file"
            )
        
        # Extract text content from the file
        try:
            content = await extract_text_from_file(file_path, file.content_type)
            logger.info(f"Extracted {len(content)} characters from file")
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to extract text from file"
            )
        
        # Validate extracted content
        if not content or len(content.strip()) < 10:
            logger.warning("Extracted content is too short or empty")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must contain at least 10 characters of text content"
            )
        
        # Determine document type from content type
        document_type_mapping = {
            "application/pdf": DocumentType.PDF,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": DocumentType.DOCX,
            "application/msword": DocumentType.DOC,
            "text/plain": DocumentType.TXT
        }
        document_type = document_type_mapping.get(file.content_type, DocumentType.TXT)
        
        # Calculate word count and reading time
        word_count = len(content.split())
        reading_time_minutes = max(1, word_count // 200)  # Assume 200 words per minute
        
        # Create ReflectionSource object
        reflection = ReflectionSource(
            title=title,
            description=description,
            content=content,
            file_path=file_path,
            file_name=file.filename,
            file_size=file_size,
            document_type=document_type,
            user_id=user_id,
            processing_status=ProcessingStatus.PENDING,
            word_count=word_count,
            reading_time_minutes=reading_time_minutes,
            auto_process=True,
            processing_priority=0
        )
        
        # Save to database
        try:
            reflection_repo = ReflectionRepository()
            created_reflection = await reflection_repo.create(reflection)
            logger.info(f"Created reflection with ID: {created_reflection.id}")
        except Exception as e:
            logger.error(f"Failed to create reflection in database: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save reflection to database"
            )
        
        # Queue for AI processing in the background
        try:
            # Import here to avoid circular imports
            from app.services.journey.insight_template_engine import process_reflection_ai
            background_tasks.add_task(process_reflection_ai, str(created_reflection.id))
            logger.info(f"Queued reflection {created_reflection.id} for AI processing")
        except ImportError:
            # If the AI service doesn't exist yet, use the placeholder
            background_tasks.add_task(process_reflection_ai, str(created_reflection.id), user_id)
            logger.info(f"Queued reflection {created_reflection.id} for AI processing (placeholder)")
        
        # Convert to response format
        response = ReflectionResponse(
            id=str(created_reflection.id),
            title=created_reflection.title,
            description=created_reflection.description,
            content=created_reflection.content,
            categories=created_reflection.categories,
            tags=created_reflection.tags,
            processing_status=created_reflection.processing_status,
            insight_count=len(created_reflection.insight_ids),
            word_count=created_reflection.word_count,
            created_at=created_reflection.created_at,
            updated_at=created_reflection.updated_at
        )
        
        logger.info(f"✅ Successfully created reflection: {created_reflection.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in upload_reflection_document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing the upload"
        )


@router.post("/{reflection_id}/insights/generate", response_model=List[InsightResponse])
async def generate_insights_from_reflection(
    reflection_id: str,
    user_info: dict = Depends(get_current_user)
):
    """
    Generate insights from a specific reflection using the AI insight template engine.
    
    This endpoint:
    1. Validates that the reflection exists and belongs to the user
    2. Uses the InsightTemplateEngine to generate insights
    3. Saves the generated insights to the database
    4. Returns the list of generated insights
    
    Args:
        reflection_id: ID of the reflection to generate insights from
        user_info: Current user information from authentication
        
    Returns:
        List[InsightResponse]: List of generated insights
        
    Raises:
        HTTPException: If reflection not found, unauthorized, or processing fails
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"=== generate_insights_from_reflection called ===")
        logger.info(f"user: {user_id}, reflection_id: {reflection_id}")
        
        # Get the reflection and verify ownership
        reflection_repo = ReflectionRepository()
        reflection = await reflection_repo.get_by_id(reflection_id)
        
        if not reflection:
            logger.warning(f"Reflection not found: {reflection_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reflection not found"
            )
        
        # Verify user owns this reflection
        if reflection.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access reflection {reflection_id} owned by {reflection.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this reflection"
            )
        
        # Check if reflection has content to analyze
        if not reflection.content or len(reflection.content.strip()) < 10:
            logger.warning(f"Reflection {reflection_id} has insufficient content for insight generation")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reflection must have at least 10 characters of content to generate insights"
            )
        
        # Initialize the insight template engine
        template_engine = InsightTemplateEngine()
        
        # Convert reflection to dict format expected by template engine
        reflection_dict = {
            'id': str(reflection.id),
            'user_id': reflection.user_id,
            'type': 'document_analysis' if reflection.document_type else 'coaching_session',
            'title': reflection.title,
            'content': reflection.content,
            'created_at': reflection.created_at.isoformat() if reflection.created_at else None,
            'themes': reflection.tags,  # Use tags as themes for now
            'document_title': reflection.title,
            'document_type': reflection.document_type.value if reflection.document_type else None
        }
        
        # Generate insights using the template engine
        logger.info(f"Generating insights for reflection {reflection_id}")
        raw_insights = template_engine.generate_insights(reflection_dict)
        
        if not raw_insights:
            logger.warning(f"No insights generated for reflection {reflection_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate insights from reflection"
            )
        
        # Save insights to database
        insight_repo = InsightRepository()
        saved_insights = []
        
        for raw_insight in raw_insights:
            try:
                # Create Insight model from raw insight data
                insight = Insight(
                    title=raw_insight.get('title', 'Generated Insight'),
                    content=raw_insight.get('details', raw_insight.get('summary', '')),
                    summary=raw_insight.get('summary', ''),
                    category=CategoryType.PERSONAL_DEVELOPMENT,  # Default category
                    subcategories=[],
                    tags=raw_insight.get('tags', []),
                    source_id=str(reflection.id),
                    source_title=reflection.title,
                    source_excerpt=raw_insight.get('source_references', [None])[0] if raw_insight.get('source_references') else None,
                    user_id=user_id,
                    review_status=ReviewStatus.DRAFT,
                    confidence_score=raw_insight.get('confidence_score', 0.5),
                    is_actionable=bool(raw_insight.get('actionable_steps')),
                    suggested_actions=raw_insight.get('actionable_steps', []),
                    processing_metadata=raw_insight.get('processing_metadata', {}),
                    ai_model_version=raw_insight.get('processing_metadata', {}).get('ai_model', 'mock_model_v1')
                )
                
                # Save to database
                saved_insight = await insight_repo.create(insight)
                saved_insights.append(saved_insight)
                logger.info(f"Saved insight: {saved_insight.id}")
                
            except Exception as e:
                logger.error(f"Error saving insight: {e}")
                # Continue with other insights even if one fails
                continue
        
        if not saved_insights:
            logger.error(f"Failed to save any insights for reflection {reflection_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save generated insights"
            )
        
        # Update reflection to mark insights as generated
        try:
            await reflection_repo.update(str(reflection.id), {
                'processing_status': ProcessingStatus.COMPLETED,
                'insight_ids': [str(insight.id) for insight in saved_insights]
            })
        except Exception as e:
            logger.warning(f"Failed to update reflection status: {e}")
            # Don't fail the request if we can't update the reflection
        
        # Convert to response format
        insight_responses = []
        for insight in saved_insights:
            response = InsightResponse(
                id=str(insight.id),
                title=insight.title,
                content=insight.content,
                summary=insight.summary,
                category=insight.category,
                subcategories=insight.subcategories,
                tags=insight.tags,
                source_id=insight.source_id,
                source_title=insight.source_title,
                source_excerpt=insight.source_excerpt,
                review_status=insight.review_status,
                confidence_score=insight.confidence_score,
                is_favorite=insight.is_favorite,
                is_actionable=insight.is_actionable,
                suggested_actions=insight.suggested_actions,
                user_rating=insight.user_rating,
                view_count=insight.view_count,
                created_at=insight.created_at,
                updated_at=insight.updated_at,
                generated_at=insight.generated_at
            )
            insight_responses.append(response)
        
        logger.info(f"✅ Successfully generated {len(insight_responses)} insights for reflection {reflection_id}")
        return insight_responses
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in generate_insights_from_reflection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating insights"
        )


@router.get("/journey/feed", response_model=JourneyFeedResponse)
async def get_journey_feed(
    categories: List[CategoryType] = Query(None, description="Filter by categories (multiple allowed)"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    user_info: dict = Depends(get_current_user)
):
    """
    Get the journey feed with insights and reflections, optionally filtered by categories.
    
    This endpoint:
    1. Retrieves insights (and potentially reflections) for the user
    2. Applies category filtering if specified (supports multiple categories)
    3. Returns paginated results with metadata
    4. Includes category counts for filter UI
    
    Args:
        categories: Optional list of categories to filter by
        skip: Number of items to skip for pagination
        limit: Maximum number of items to return
        user_info: Current user information from authentication
        
    Returns:
        JourneyFeedResponse: Paginated feed items with metadata
    """
    try:
        user_id = user_info['clerk_user_id']
        logger.info(f"=== get_journey_feed called ===")
        logger.info(f"user: {user_id}, categories: {categories}, skip: {skip}, limit: {limit}")
        
        insight_repo = InsightRepository()
        
        # Get insights based on category filter
        if categories:
            insights = await insight_repo.get_by_categories(user_id, categories, skip, limit)
            total_count = await insight_repo.count_by_categories_for_user(user_id, categories)
        else:
            insights = await insight_repo.get_all_for_user(user_id, skip, limit)
            total_count = await insight_repo.count_for_user(user_id)
        
        # Convert insights to feed items
        feed_items = []
        for insight in insights:
            feed_item = JourneyFeedItem(
                type="insight",
                id=str(insight.id),
                title=insight.title,
                content=insight.content,
                summary=insight.summary,
                category=insight.category,
                tags=insight.tags,
                review_status=insight.review_status,
                source_id=insight.source_id,
                source_title=insight.source_title,
                is_favorite=insight.is_favorite,
                is_actionable=insight.is_actionable,
                suggested_actions=insight.suggested_actions,
                confidence_score=insight.confidence_score,
                user_rating=insight.user_rating,
                view_count=insight.view_count,
                created_at=insight.created_at,
                updated_at=insight.updated_at,
                generated_at=insight.generated_at
            )
            feed_items.append(feed_item)
        
        # Get category counts for filter UI
        try:
            category_counts = await insight_repo.get_category_counts(user_id)
        except Exception as e:
            logger.warning(f"Failed to get category counts: {e}")
            category_counts = {}
        
        # Create response
        response = JourneyFeedResponse(
            items=feed_items,
            total_count=total_count,
            skip=skip,
            limit=limit,
            category_counts=category_counts
        )
        
        logger.info(f"✅ Successfully retrieved {len(feed_items)} feed items (total: {total_count})")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in get_journey_feed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving the journey feed"
        )