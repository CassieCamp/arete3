from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.goal import (
    GoalResponse, GoalCreateRequest, GoalUpdateRequest, 
    ProgressUpdateRequest, GoalSuggestionResponse, 
    SuccessVisionSuggestionResponse, ProgressEntryResponse
)
from app.services.goal_service import GoalService
from app.api.v1.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new goal with human-centered structure"""
    logger.info(f"=== POST /goals called ===")
    logger.info(f"Creating goal for user: {current_user.get('user_id')}")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        goal = await goal_service.create_goal(user_id, goal_data.dict())
        
        # Convert to response format
        return GoalResponse(
            id=str(goal.id),
            user_id=goal.user_id,
            goal_statement=goal.goal_statement,
            success_vision=goal.success_vision,
            progress_emoji=goal.progress_emoji,
            progress_notes=goal.progress_notes,
            progress_history=[
                ProgressEntryResponse(
                    emoji=entry.emoji,
                    notes=entry.notes,
                    timestamp=entry.timestamp
                ) for entry in (goal.progress_history or [])
            ],
            ai_suggested=goal.ai_suggested,
            source_documents=goal.source_documents,
            status=goal.status,
            tags=goal.tags,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )
        
    except Exception as e:
        logger.error(f"❌ Error creating goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create goal: {str(e)}"
        )


@router.get("/", response_model=List[GoalResponse])
async def get_user_goals(
    current_user: dict = Depends(get_current_user)
):
    """Get all goals for the current user"""
    logger.info(f"=== GET /goals called ===")
    logger.info(f"Getting goals for user: {current_user.get('user_id')}")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        goals = await goal_service.get_all_user_goals(user_id)
        
        return [
            GoalResponse(
                id=str(goal.id),
                user_id=goal.user_id,
                goal_statement=goal.goal_statement,
                success_vision=goal.success_vision,
                progress_emoji=goal.progress_emoji,
                progress_notes=goal.progress_notes,
                progress_history=[
                    ProgressEntryResponse(
                        emoji=entry.emoji,
                        notes=entry.notes,
                        timestamp=entry.timestamp
                    ) for entry in (goal.progress_history or [])
                ],
                ai_suggested=goal.ai_suggested,
                source_documents=goal.source_documents,
                status=goal.status,
                tags=goal.tags,
                created_at=goal.created_at,
                updated_at=goal.updated_at
            ) for goal in goals
        ]
        
    except Exception as e:
        logger.error(f"❌ Error getting user goals: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goals: {str(e)}"
        )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific goal by ID"""
    logger.info(f"=== GET /goals/{goal_id} called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        goal = await goal_service.get_goal(goal_id, user_id)
        
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return GoalResponse(
            id=str(goal.id),
            user_id=goal.user_id,
            goal_statement=goal.goal_statement,
            success_vision=goal.success_vision,
            progress_emoji=goal.progress_emoji,
            progress_notes=goal.progress_notes,
            progress_history=[
                ProgressEntryResponse(
                    emoji=entry.emoji,
                    notes=entry.notes,
                    timestamp=entry.timestamp
                ) for entry in (goal.progress_history or [])
            ],
            ai_suggested=goal.ai_suggested,
            source_documents=goal.source_documents,
            status=goal.status,
            tags=goal.tags,
            created_at=goal.created_at,
            updated_at=goal.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal: {str(e)}"
        )


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update a goal"""
    logger.info(f"=== PUT /goals/{goal_id} called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        
        # Filter out None values
        update_data = {k: v for k, v in goal_data.dict().items() if v is not None}
        
        updated_goal = await goal_service.update_goal(goal_id, user_id, update_data)
        
        if not updated_goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return GoalResponse(
            id=str(updated_goal.id),
            user_id=updated_goal.user_id,
            goal_statement=updated_goal.goal_statement,
            success_vision=updated_goal.success_vision,
            progress_emoji=updated_goal.progress_emoji,
            progress_notes=updated_goal.progress_notes,
            progress_history=[
                ProgressEntryResponse(
                    emoji=entry.emoji,
                    notes=entry.notes,
                    timestamp=entry.timestamp
                ) for entry in (updated_goal.progress_history or [])
            ],
            ai_suggested=updated_goal.ai_suggested,
            source_documents=updated_goal.source_documents,
            status=updated_goal.status,
            tags=updated_goal.tags,
            created_at=updated_goal.created_at,
            updated_at=updated_goal.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update goal: {str(e)}"
        )


@router.post("/{goal_id}/progress", response_model=GoalResponse)
async def update_progress(
    goal_id: str,
    progress_data: ProgressUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update goal progress with emoji and notes"""
    logger.info(f"=== POST /goals/{goal_id}/progress called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        
        updated_goal = await goal_service.update_progress_emotion(
            goal_id, user_id, progress_data.emoji, progress_data.notes
        )
        
        if not updated_goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
        return GoalResponse(
            id=str(updated_goal.id),
            user_id=updated_goal.user_id,
            goal_statement=updated_goal.goal_statement,
            success_vision=updated_goal.success_vision,
            progress_emoji=updated_goal.progress_emoji,
            progress_notes=updated_goal.progress_notes,
            progress_history=[
                ProgressEntryResponse(
                    emoji=entry.emoji,
                    notes=entry.notes,
                    timestamp=entry.timestamp
                ) for entry in (updated_goal.progress_history or [])
            ],
            ai_suggested=updated_goal.ai_suggested,
            source_documents=updated_goal.source_documents,
            status=updated_goal.status,
            tags=updated_goal.tags,
            created_at=updated_goal.created_at,
            updated_at=updated_goal.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update progress: {str(e)}"
        )


@router.get("/{goal_id}/progress", response_model=List[ProgressEntryResponse])
async def get_progress_timeline(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get progress timeline for a goal"""
    logger.info(f"=== GET /goals/{goal_id}/progress called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        progress_timeline = await goal_service.get_progress_timeline(goal_id, user_id)
        
        return [
            ProgressEntryResponse(
                emoji=entry.emoji,
                notes=entry.notes,
                timestamp=entry.timestamp
            ) for entry in progress_timeline
        ]
        
    except Exception as e:
        logger.error(f"❌ Error getting progress timeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get progress timeline: {str(e)}"
        )


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a goal"""
    logger.info(f"=== DELETE /goals/{goal_id} called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        success = await goal_service.delete_goal(goal_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete goal: {str(e)}"
        )


@router.post("/suggestions", response_model=List[GoalSuggestionResponse])
async def get_goal_suggestions(
    document_ids: List[str],
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered goal suggestions based on documents"""
    logger.info(f"=== POST /goals/suggestions called ===")
    
    try:
        goal_service = GoalService()
        user_id = current_user["user_id"]
        suggestions = await goal_service.suggest_goals_from_documents(user_id, document_ids)
        
        return [
            GoalSuggestionResponse(
                goal_statement=suggestion.goal_statement,
                success_vision=suggestion.success_vision,
                source_documents=suggestion.source_documents
            ) for suggestion in suggestions
        ]
        
    except Exception as e:
        logger.error(f"❌ Error getting goal suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goal suggestions: {str(e)}"
        )


@router.post("/success-vision-suggestions", response_model=SuccessVisionSuggestionResponse)
async def get_success_vision_suggestions(
    goal_statement: str,
    current_user: dict = Depends(get_current_user)
):
    """Get success vision suggestions for a goal statement"""
    logger.info(f"=== POST /goals/success-vision-suggestions called ===")
    
    try:
        goal_service = GoalService()
        user_context = {"user_id": current_user["user_id"]}
        suggestions = await goal_service.enhance_success_vision(goal_statement, user_context)
        
        return SuccessVisionSuggestionResponse(suggestions=suggestions)
        
    except Exception as e:
        logger.error(f"❌ Error getting success vision suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get success vision suggestions: {str(e)}"
        )