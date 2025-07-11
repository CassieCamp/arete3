from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import Optional, List
from app.api.v1.deps import get_current_user_clerk_id
from app.schemas.entry import (
    EntryCreateRequest,
    EntryResponse,
    EntryDetailResponse,
    EntryListResponse,
    AcceptGoalsRequest,
    FreemiumStatusResponse
)
from app.services.entry_service import EntryService
from app.services.freemium_service import FreemiumService
from app.services.text_extraction_service import TextExtractionService
from app.models.entry import EntryType
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _convert_to_response(entry) -> EntryResponse:
    """Convert Entry model to response format"""
    return EntryResponse(
        id=str(entry.id),
        entry_type=entry.entry_type.value,
        title=entry.title or "Untitled Entry",
        client_user_id=entry.client_user_id,
        coach_user_id=entry.coach_user_id,
        coaching_relationship_id=entry.coaching_relationship_id,
        session_date=entry.session_date.isoformat() if entry.session_date else None,
        status=entry.status.value,
        created_at=entry.created_at.isoformat(),
        updated_at=entry.updated_at.isoformat(),
        completed_at=entry.completed_at.isoformat() if entry.completed_at else None,
        detected_goals=entry.detected_goals,
        has_insights=len(entry.celebrations) > 0 or len(entry.intentions) > 0 or len(entry.client_discoveries) > 0
    )


def _convert_to_detail_response(entry) -> EntryDetailResponse:
    """Convert Entry model to detailed response format"""
    base_response = _convert_to_response(entry)
    
    return EntryDetailResponse(
        **base_response.model_dump(),
        content=entry.content,
        transcript_content=entry.transcript_content,
        celebrations=[c.model_dump() for c in entry.celebrations],
        intentions=[i.model_dump() for i in entry.intentions],
        client_discoveries=[d.model_dump() for d in entry.client_discoveries],
        goal_progress=[g.model_dump() for g in entry.goal_progress],
        coaching_presence=entry.coaching_presence.model_dump() if entry.coaching_presence else None,
        powerful_questions=[q.model_dump() for q in entry.powerful_questions],
        action_items=[a.model_dump() for a in entry.action_items],
        emotional_shifts=[e.model_dump() for e in entry.emotional_shifts],
        values_beliefs=[v.model_dump() for v in entry.values_beliefs],
        communication_patterns=entry.communication_patterns.model_dump() if entry.communication_patterns else None
    )


@router.post("/", response_model=EntryResponse)
async def create_entry(
    request: EntryCreateRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Create a new entry (session or fresh thought).
    
    Supports both paired (with coaching relationship) and unpaired entries.
    Includes freemium gating to limit non-coached users to 3 entries.
    """
    try:
        logger.info(f"=== create_entry called ===")
        logger.info(f"user: {current_user_id}, type: {request.entry_type}")
        
        # Check freemium limits
        freemium_service = FreemiumService()
        can_create = await freemium_service.can_create_entry(current_user_id)
        
        if not can_create:
            freemium_status = await freemium_service.get_freemium_status(current_user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Entry limit reached",
                    "freemium_status": freemium_status
                }
            )
        
        # Validate content length
        if len(request.content.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Entry content must be at least 10 characters long"
            )
        
        # Create entry
        entry_service = EntryService()
        entry = await entry_service.create_entry(
            user_id=current_user_id,
            entry_type=request.entry_type,
            content=request.content,
            title=request.title,
            coaching_relationship_id=request.coaching_relationship_id,
            session_date=request.session_date
        )
        
        # Increment entry count for freemium users
        await freemium_service.increment_entry_count(current_user_id)
        
        # Convert to response format
        response = _convert_to_response(entry)
        logger.info(f"✅ Successfully created entry: {entry.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create entry"
        )


@router.post("/upload", response_model=EntryResponse)
async def create_entry_from_file(
    entry_type: str = Form(...),
    session_date: str = Form(...),
    input_method: str = Form("upload"),
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Create a new entry from an uploaded file (supports PDF and text files).
    
    This endpoint handles file uploads for entry creation, extracting text
    from PDF files using the text extraction service.
    """
    try:
        logger.info(f"=== create_entry_from_file called ===")
        logger.info(f"user: {current_user_id}, type: {entry_type}, file: {file.filename}")
        
        # Validate entry type
        try:
            parsed_entry_type = EntryType(entry_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid entry type: {entry_type}"
            )
        
        # Check freemium limits
        freemium_service = FreemiumService()
        can_create = await freemium_service.can_create_entry(current_user_id)
        
        if not can_create:
            freemium_status = await freemium_service.get_freemium_status(current_user_id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Entry limit reached",
                    "freemium_status": freemium_status
                }
            )
        
        # Validate file type and size
        allowed_types = ["text/plain", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Check file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        file_content = await file.read()
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 5MB"
            )
        
        # Extract text from file
        if file.content_type == "text/plain":
            # For text files, decode directly
            content = file_content.decode('utf-8')
        else:
            # For PDF files, use text extraction service
            text_extraction_service = TextExtractionService()
            content = await text_extraction_service.extract_text_from_bytes(
                file_content,
                file.filename or "uploaded_file.pdf"
            )
        
        # Validate content length
        if len(content.strip()) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Extracted content must be at least 10 characters long"
            )
        
        # Create entry
        entry_service = EntryService()
        entry = await entry_service.create_entry(
            user_id=current_user_id,
            entry_type=parsed_entry_type,
            content=content,
            title=title,
            coaching_relationship_id=None,  # File uploads are typically unpaired
            session_date=session_date
        )
        
        # Increment entry count for freemium users
        await freemium_service.increment_entry_count(current_user_id)
        
        # Convert to response format
        response = _convert_to_response(entry)
        logger.info(f"✅ Successfully created entry from file: {entry.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating entry from file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create entry from file"
        )


@router.get("/", response_model=EntryListResponse)
async def get_entries(
    entry_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get entries for the current user with optional filtering.
    
    Includes freemium gating for entry access.
    """
    try:
        logger.info(f"=== get_entries called ===")
        logger.info(f"user: {current_user_id}, type: {entry_type}")
        
        # Parse entry type
        parsed_entry_type = None
        if entry_type:
            try:
                parsed_entry_type = EntryType(entry_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid entry type: {entry_type}"
                )
        
        # Get entries
        entry_service = EntryService()
        entries = await entry_service.get_entries(
            user_id=current_user_id,
            entry_type=parsed_entry_type,
            limit=limit,
            offset=offset
        )
        
        # Get total count and freemium status
        freemium_service = FreemiumService()
        freemium_status = await freemium_service.get_freemium_status(current_user_id)
        
        # Check if results are limited due to freemium
        freemium_limited = not freemium_status.get("has_coach", False) and len(entries) >= 3
        
        # Convert to response format
        entry_responses = [_convert_to_response(entry) for entry in entries]
        
        response = EntryListResponse(
            entries=entry_responses,
            total_count=len(entries),
            has_more=len(entries) == limit,
            freemium_limited=freemium_limited
        )
        
        logger.info(f"✅ Successfully retrieved {len(entries)} entries")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve entries"
        )


@router.get("/{entry_id}", response_model=EntryDetailResponse)
async def get_entry_detail(
    entry_id: str,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get detailed view of a specific entry.
    
    Includes freemium gating for detailed insights.
    """
    try:
        logger.info(f"=== get_entry_detail called ===")
        logger.info(f"user: {current_user_id}, entry: {entry_id}")
        
        entry_service = EntryService()
        entry = await entry_service.get_entry_insights(entry_id, current_user_id)
        
        if not entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found"
            )
        
        # Convert to detailed response format
        response = _convert_to_detail_response(entry)
        logger.info(f"✅ Successfully retrieved entry detail")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting entry detail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve entry detail"
        )


@router.post("/{entry_id}/accept-goals", response_model=dict)
async def accept_detected_goals(
    entry_id: str,
    request: AcceptGoalsRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Accept detected goals from an entry and convert them to destinations.
    """
    try:
        logger.info(f"=== accept_detected_goals called ===")
        logger.info(f"entry: {entry_id}, user: {current_user_id}")
        
        entry_service = EntryService()
        success = await entry_service.accept_detected_goals(
            entry_id=entry_id,
            user_id=current_user_id,
            accepted_goal_indices=request.accepted_goal_indices
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Entry not found or goals could not be accepted"
            )
        
        logger.info(f"✅ Successfully accepted {len(request.accepted_goal_indices)} goals")
        return {"message": f"Successfully accepted {len(request.accepted_goal_indices)} goals"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error accepting goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept goals"
        )


@router.get("/freemium/status", response_model=FreemiumStatusResponse)
async def get_freemium_status(
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Get freemium status for entry creation.
    """
    try:
        logger.info(f"=== get_freemium_status called ===")
        logger.info(f"user: {current_user_id}")
        
        freemium_service = FreemiumService()
        status_data = await freemium_service.get_freemium_status(current_user_id)
        
        response = FreemiumStatusResponse(
            has_coach=status_data.get("has_coach", False),
            entries_count=status_data.get("entries_count", 0),
            max_free_entries=status_data.get("max_free_entries", 3),
            entries_remaining=status_data.get("entries_remaining", 0),
            can_create_entries=status_data.get("can_create_entries", False),
            can_access_insights=status_data.get("can_access_insights", False),
            is_freemium=status_data.get("is_freemium", True)
        )
        
        logger.info(f"✅ Successfully retrieved freemium status")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error getting freemium status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve freemium status"
        )