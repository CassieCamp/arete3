from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Optional, List
from app.api.v1.deps import get_current_user_clerk_id
from app.schemas.session_insight import (
    SessionInsightCreateRequest, 
    SessionInsightResponse, 
    SessionInsightDetailResponse,
    SessionInsightListResponse,
    SessionInsightUpdateRequest
)
from app.services.session_insight_service import SessionInsightService
from app.services.text_extraction_service import TextExtractionService
from app.repositories.profile_repository import ProfileRepository
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _convert_to_response(insight) -> SessionInsightResponse:
    """Convert SessionInsight model to response format"""
    return SessionInsightResponse(
        id=str(insight.id),
        coaching_relationship_id=insight.coaching_relationship_id,
        client_user_id=insight.client_user_id,
        coach_user_id=insight.coach_user_id,
        session_date=insight.session_date.isoformat() if insight.session_date else None,
        session_title=insight.session_title,
        session_summary=insight.session_summary,
        key_themes=insight.key_themes,
        overall_session_quality=insight.overall_session_quality,
        status=insight.status.value,
        created_at=insight.created_at.isoformat(),
        completed_at=insight.completed_at.isoformat() if insight.completed_at else None,
        celebration_count=1 if insight.celebration else 0,
        intention_count=1 if insight.intention else 0,
        discovery_count=len(insight.client_discoveries),
        action_item_count=len(insight.action_items)
    )


def _convert_to_detail_response(insight) -> SessionInsightDetailResponse:
    """Convert SessionInsight model to detailed response format"""
    base_response = _convert_to_response(insight)
    
    return SessionInsightDetailResponse(
        **base_response.model_dump(),
        celebration=insight.celebration.model_dump() if insight.celebration else None,
        intention=insight.intention.model_dump() if insight.intention else None,
        client_discoveries=[d.model_dump() for d in insight.client_discoveries],
        goal_progress=[g.model_dump() for g in insight.goal_progress],
        coaching_presence=insight.coaching_presence.model_dump() if insight.coaching_presence else None,
        powerful_questions=[q.model_dump() for q in insight.powerful_questions],
        action_items=[a.model_dump() for a in insight.action_items],
        emotional_shifts=[e.model_dump() for e in insight.emotional_shifts],
        values_beliefs=[v.model_dump() for v in insight.values_beliefs],
        communication_patterns=insight.communication_patterns.model_dump() if insight.communication_patterns else None
    )


@router.post("/", response_model=SessionInsightResponse)
async def create_session_insight_from_file(
    coaching_relationship_id: str = Form(...),
    session_date: Optional[str] = Form(None),
    session_title: Optional[str] = Form(None),
    transcript_file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Create session insight from uploaded transcript file.
    
    Supports common text file formats (txt, docx, pdf) and processes
    them through the existing document processing pipeline.
    """
    try:
        logger.info(f"=== create_session_insight_from_file called ===")
        logger.info(f"user: {current_user_id}, relationship: {coaching_relationship_id}")
        
        # Validate file type and size
        allowed_types = ["text/plain", "application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
        if transcript_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        file_content = await transcript_file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit"
            )
        
        # Extract text from file
        text_extraction_service = TextExtractionService()
        transcript_content = await text_extraction_service.extract_text_from_bytes(
            file_content, 
            transcript_file.filename or "transcript.txt"
        )
        
        if not transcript_content or len(transcript_content.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript content is too short or could not be extracted"
            )
        
        # Create session insight
        session_insight_service = SessionInsightService()
        insight = await session_insight_service.create_insight_from_transcript(
            coaching_relationship_id=coaching_relationship_id,
            transcript_content=transcript_content,
            created_by=current_user_id,
            session_date=session_date,
            session_title=session_title
        )
        
        # Convert to response format
        response = _convert_to_response(insight)
        logger.info(f"✅ Successfully created session insight: {insight.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating session insight from file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process transcript file"
        )


@router.post("/from-text", response_model=SessionInsightResponse) 
async def create_session_insight_from_text(
    request: SessionInsightCreateRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Create session insight from pasted transcript text.
    
    Alternative to file upload for direct text input.
    """
    try:
        logger.info(f"=== create_session_insight_from_text called ===")
        logger.info(f"user: {current_user_id}, relationship: {request.coaching_relationship_id}")
        
        if not request.transcript_text or len(request.transcript_text.strip()) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript text is required and must be at least 50 characters"
            )
        
        # Create session insight
        session_insight_service = SessionInsightService()
        insight = await session_insight_service.create_insight_from_transcript(
            coaching_relationship_id=request.coaching_relationship_id,
            transcript_content=request.transcript_text,
            created_by=current_user_id,
            session_date=request.session_date,
            session_title=request.session_title
        )
        
        # Convert to response format
        response = _convert_to_response(insight)
        logger.info(f"✅ Successfully created session insight: {insight.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating session insight from text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process transcript text"
        )


@router.get("/relationship/{relationship_id}", response_model=SessionInsightListResponse)
async def get_session_insights_for_relationship(
    relationship_id: str,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get all session insights for a coaching relationship.
    
    Returns paginated list of insights ordered by session date (newest first).
    Includes summary data and insight counts for list display.
    """
    try:
        logger.info(f"=== get_session_insights_for_relationship called ===")
        logger.info(f"user: {current_user_id}, relationship: {relationship_id}")
        
        session_insight_service = SessionInsightService()
        insights = await session_insight_service.get_insights_for_relationship(
            relationship_id=relationship_id,
            requesting_user_id=current_user_id,
            limit=limit,
            offset=offset
        )
        
        # Get total count
        total_count = await session_insight_service.insight_repository.get_insights_count_by_relationship(
            relationship_id
        )
        
        # Get relationship details for names
        relationship = await session_insight_service.relationship_repository.get_relationship_by_id(
            relationship_id
        )
        
        # Get profile names
        profile_repository = ProfileRepository()
        coach_profile = await profile_repository.get_profile_by_clerk_id(relationship.coach_user_id)
        client_profile = await profile_repository.get_profile_by_clerk_id(relationship.client_user_id)
        
        coach_name = f"{coach_profile.first_name} {coach_profile.last_name}" if coach_profile else "Unknown Coach"
        client_name = f"{client_profile.first_name} {client_profile.last_name}" if client_profile else "Unknown Client"
        
        # Convert insights to response format
        insight_responses = [_convert_to_response(insight) for insight in insights]
        
        response = SessionInsightListResponse(
            insights=insight_responses,
            total_count=total_count,
            relationship_id=relationship_id,
            client_name=client_name,
            coach_name=coach_name
        )
        
        logger.info(f"✅ Successfully retrieved {len(insights)} insights")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting insights for relationship: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session insights"
        )


@router.get("/{insight_id}", response_model=SessionInsightDetailResponse)
async def get_session_insight_detail(
    insight_id: str,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get detailed view of a specific session insight.
    
    Returns complete insight data including all ICF-aligned analysis sections.
    """
    try:
        logger.info(f"=== get_session_insight_detail called ===")
        logger.info(f"user: {current_user_id}, insight: {insight_id}")
        
        session_insight_service = SessionInsightService()
        insight = await session_insight_service.get_insight_by_id(
            insight_id=insight_id,
            requesting_user_id=current_user_id
        )
        
        if not insight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session insight not found"
            )
        
        # Convert to detailed response format
        response = _convert_to_detail_response(insight)
        logger.info(f"✅ Successfully retrieved insight detail")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting insight detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session insight detail"
        )


@router.delete("/{insight_id}")
async def delete_session_insight(
    insight_id: str,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Delete a session insight.
    
    Only the creator or coach in the relationship can delete insights.
    """
    try:
        logger.info(f"=== delete_session_insight called ===")
        logger.info(f"user: {current_user_id}, insight: {insight_id}")
        
        session_insight_service = SessionInsightService()
        success = await session_insight_service.delete_insight(
            insight_id=insight_id,
            requesting_user_id=current_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session insight not found"
            )
        
        logger.info(f"✅ Successfully deleted insight")
        return {"message": "Session insight deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting insight: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session insight"
        )