from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from typing import List
import logging
from datetime import datetime

from app.api.v1.deps import get_current_user_clerk_id
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
    user_info: dict = Depends(get_current_user_clerk_id),
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
    user_info: dict = Depends(get_current_user_clerk_id),
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
        ai_analysis_result = None
        processing_status = ProcessingStatus.PROCESSING
        ai_processing_completed_at = None
        generated_title = file.filename or "Untitled Document"
        
        if text_content and text_content.strip():
            logger.info("Starting AI analysis of extracted text")
            ai_analysis_result = await analyze_text_for_insights(text_content)
            processing_status = ProcessingStatus.COMPLETED
            ai_processing_completed_at = datetime.utcnow()
            
            # Extract the generated title from AI analysis
            if ai_analysis_result and ai_analysis_result.get("title"):
                generated_title = ai_analysis_result["title"]
                logger.info(f"✅ AI generated title: {generated_title}")
            
            logger.info("✅ AI analysis completed successfully")
        else:
            logger.warning("No text content available for AI analysis")
            processing_status = ProcessingStatus.COMPLETED
        
        # 6. Create DocumentAnalysis object from AI result
        document_analysis = None
        if ai_analysis_result:
            from app.models.journey.reflection import DocumentAnalysis
            document_analysis = DocumentAnalysis(
                summary=ai_analysis_result.get("summary", ""),
                key_themes=ai_analysis_result.get("key_themes", []),
                sentiment=ai_analysis_result.get("sentiment", "neutral"),
                sentiment_score=ai_analysis_result.get("sentiment_score", 0.0),
                entities=ai_analysis_result.get("entities", {}),
                categorized_insights=ai_analysis_result.get("categorized_insights") # Add this line
            )
        
        # 7. Create ReflectionSource record with complete data including AI analysis
        reflection = ReflectionSource(
            user_id=user_id,
            title=generated_title,  # Use AI-generated title instead of filename
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
        
        # 8. Save to database
        created_reflection = await reflection_repo.create(reflection)
        logger.info(f"Reflection created successfully with ID: {created_reflection.id}")
        
        # 9. Create individual Insight records from categorized insights
        if ai_analysis_result and ai_analysis_result.get("categorized_insights"):
            await _create_insights_from_analysis(
                created_reflection,
                ai_analysis_result["categorized_insights"],
                user_id
            )
            logger.info("✅ Individual insights created successfully")
        
        return created_reflection
        
    except HTTPException:
        # Re-raise HTTP exceptions from file storage service
        raise
    except Exception as e:
        logger.error(f"Upload failed for user {user_id}, file {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document upload: {str(e)}"
        )

@router.get("/insights", response_model=dict)
async def get_insights(
    user_info: dict = Depends(get_current_user_clerk_id),
    reflection_repo: ReflectionSourceRepository = Depends(get_reflection_repository)
):
    """
    Get real insights data from the database for the user's journey feed.
    
    This endpoint returns actual ReflectionSource documents from the database
    with proper categorized insights mapping for the frontend.
    """
    user_id = user_info['clerk_user_id']
    logger.info(f"Getting insights for user: {user_id}")
    
    # Fetch all ReflectionSource documents for the user from the database
    reflections = await reflection_repo.get_by_user_id(user_id)
    
    # Convert ReflectionSource objects to the format expected by frontend
    insights = []
    for reflection in reflections:
        # Extract categorized insights from document_analysis.entities
        insights_by_category = {}
        categorized_insights = None
        
        if (reflection.document_analysis and
            hasattr(reflection.document_analysis, 'categorized_insights') and
            reflection.document_analysis.categorized_insights):
            categorized_insights = reflection.document_analysis.categorized_insights
        
        # Map categorized insights to frontend format using new emoji system
        if categorized_insights and isinstance(categorized_insights, dict):
            category_mapping = {
                "🪞 Understanding Myself": "understanding_myself",
                "👥 Navigating Relationships": "navigating_relationships",
                "💪 Optimizing Performance": "optimizing_performance",
                "🎯 Making Progress": "making_progress"
            }
            
            for ai_category, frontend_key in category_mapping.items():
                if ai_category in categorized_insights:
                    insights_list = categorized_insights[ai_category]
                    if insights_list and isinstance(insights_list, list):
                        insights_by_category[frontend_key] = [
                            item.get('insight', '') if isinstance(item, dict) else str(item)
                            for item in insights_list if item
                        ]
            
        insight_data = {
            "id": str(reflection.id),
            "title": reflection.title,  # Use AI-generated title directly
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
            "updated_at": reflection.updated_at.isoformat() if reflection.updated_at else "",
            "insights_by_category": insights_by_category  # Add categorized insights with new emoji system
        }
        insights.append(insight_data)
    
    response = {
        "data": {
            "insights": insights,
            "reflections": insights  # Also provide as reflections for compatibility
        }
    }
    
    logger.info(f"✅ Successfully retrieved {len(insights)} insights from database")
    return response

async def _create_insights_from_analysis(
    reflection: ReflectionSource,
    categorized_insights: dict,
    user_id: str
) -> None:
    """
    Create individual Insight records from the AI categorized insights.
    
    Args:
        reflection: The reflection source that generated the insights
        categorized_insights: Dictionary of insights by category
        user_id: User ID for the insights
    """
    from app.models.journey.insight import Insight
    from app.models.journey.enums import CategoryType, ReviewStatus
    from app.repositories.journey.insight_repository import InsightRepository
    
    insight_repo = InsightRepository()
    
    # Map category names to CategoryType enums
    category_mapping = {
        "🪞 Understanding Myself": CategoryType.PERSONAL_GROWTH,
        "👥 Navigating Relationships": CategoryType.RELATIONSHIPS,
        "💪 Optimizing Performance": CategoryType.GOALS_ACHIEVEMENT,
        "🎯 Making Progress": CategoryType.CHALLENGES
    }
    
    created_insights = []
    
    for category_name, insights_list in categorized_insights.items():
        if not insights_list:  # Skip empty categories
            continue
            
        category_type = category_mapping.get(category_name, CategoryType.PERSONAL_GROWTH)
        
        for insight_data in insights_list:
            # Create Insight object with new emoji system categories
            insight = Insight(
                user_id=user_id,
                title=f"{category_name}: {insight_data.get('insight', 'Generated Insight')[:50]}...",
                content=insight_data.get('insight', 'No insight content available'),
                summary=insight_data.get('evidence', '')[:200] + "..." if len(insight_data.get('evidence', '')) > 200 else insight_data.get('evidence', ''),
                category=category_type,
                subcategories=[],
                tags=[category_name.replace('🪞 ', '').replace('👥 ', '').replace('💪 ', '').replace('🎯 ', '').lower().replace(' ', '_')],
                source_id=str(reflection.id),
                source_title=reflection.title,
                source_excerpt=insight_data.get('evidence', '')[:300],
                review_status=ReviewStatus.DRAFT,
                confidence_score=float(insight_data.get('confidence', 0.5)),
                is_favorite=False,
                is_archived=False,
                user_rating=None,
                view_count=0,
                is_actionable=True,  # AI insights are generally actionable
                suggested_actions=[],
                ai_model_version="enhanced_v1",
                processing_metadata={
                    "category": category_name,
                    "original_evidence": insight_data.get('evidence', ''),
                    "confidence": insight_data.get('confidence', 0.5)
                },
                generated_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save insight to database
            created_insight = await insight_repo.create(insight)
            created_insights.append(str(created_insight.id))
            
            logger.info(f"Created insight: {created_insight.title}")
    
    # Update reflection with insight IDs
    if created_insights:
        reflection_repo = ReflectionSourceRepository()
        for insight_id in created_insights:
            await reflection_repo.add_insight_id(str(reflection.id), insight_id)
        logger.info(f"Added {len(created_insights)} insight IDs to reflection")


@router.get("/journey/feed", response_model=JourneyFeedResponse)
async def get_journey_feed(
    user_info: dict = Depends(get_current_user_clerk_id),
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