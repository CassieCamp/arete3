from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.schemas.analysis import BaselineGenerationRequest, BaselineResponse
from app.services.analysis_service import AnalysisService
from app.services.user_service import UserService
from app.repositories.baseline_repository import BaselineRepository
from app.repositories.document_repository import DocumentRepository
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-baseline", response_model=BaselineResponse)
async def generate_baseline(
    request: BaselineGenerationRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Generate a baseline analysis for a user.
    
    This endpoint triggers the baseline generation process using the AnalysisService.
    It requires authentication and will generate a baseline for the specified user.
    """
    try:
        logger.info(f"=== Generate baseline endpoint called ===")
        logger.info(f"current_user_id: {current_user_id}, target_user_id: {request.user_id}")
        
        # Get requesting user
        user_service = UserService()
        requesting_user = await user_service.get_user_by_clerk_id(current_user_id)
        if not requesting_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requesting user not found"
            )
        
        # Get target user
        target_user = await user_service.get_user_by_id(request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # Initialize services
        baseline_repository = BaselineRepository()
        document_repository = DocumentRepository()
        analysis_service = AnalysisService(baseline_repository, document_repository)
        
        # Generate baseline
        baseline = await analysis_service.generate_client_baseline(
            user_id=request.user_id,
            clerk_user_id=target_user.clerk_user_id,
            generated_by=str(requesting_user.id),
            document_ids=request.document_ids
        )
        
        logger.info(f"✅ Generated baseline with ID: {baseline.id}")
        
        # Extract key themes from personality insights
        key_themes = []
        if baseline.personality_insights:
            key_themes = [insight.trait for insight in baseline.personality_insights[:5]]  # Top 5 themes
        
        # Calculate document count from metadata or source documents
        document_count = 0
        if baseline.metadata and hasattr(baseline.metadata, 'document_count'):
            document_count = baseline.metadata.document_count
        elif baseline.source_document_ids:
            document_count = len(baseline.source_document_ids)
        
        return BaselineResponse(
            id=str(baseline.id),
            user_id=baseline.user_id,
            executive_summary=baseline.executive_summary,
            status=baseline.status,
            created_at=baseline.created_at.isoformat(),
            completed_at=baseline.completed_at.isoformat() if baseline.completed_at else None,
            strengths=baseline.strengths or [],
            development_opportunities=baseline.development_opportunities or [],
            key_themes=key_themes,
            development_areas=baseline.development_opportunities or [],  # Alias
            summary=baseline.executive_summary,  # Alias
            document_count=document_count,
            goal_count=0,  # TODO: Implement goal counting if needed
            generated_at=baseline.created_at.isoformat()  # Alias
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error generating baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Error generating baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate baseline"
        )


@router.get("/baseline/{user_id}", response_model=Optional[BaselineResponse])
async def get_baseline(
    user_id: str,
    current_user_id: str = Depends(get_current_user_clerk_id)
):
    """
    Retrieve the most recent baseline for a specific user.
    
    This endpoint allows retrieving a user's baseline. Users can only access their own
    baseline unless they have appropriate permissions.
    """
    try:
        logger.info(f"Retrieving baseline for user: {user_id}, requested by: {current_user_id}")
        
        # Get requesting user
        user_service = UserService()
        requesting_user = await user_service.get_user_by_clerk_id(current_user_id)
        if not requesting_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requesting user not found"
            )
        
        # Get target user
        target_user = await user_service.get_user_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # For now, users can only access their own baseline
        # TODO: Add coach access permissions in future iterations
        if user_id != str(requesting_user.id):
            logger.warning(f"User {current_user_id} attempted to access baseline for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own baseline"
            )
        
        # Initialize repository and retrieve baseline
        baseline_repository = BaselineRepository()
        baseline = await baseline_repository.get_baseline_by_user_id(user_id)
        
        if baseline is None:
            logger.info(f"No baseline found for user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Baseline not found for this user"
            )
        
        logger.info(f"Successfully retrieved baseline for user: {user_id}")
        
        # Extract key themes from personality insights
        key_themes = []
        if baseline.personality_insights:
            key_themes = [insight.trait for insight in baseline.personality_insights[:5]]  # Top 5 themes
        
        # Calculate document count from metadata or source documents
        document_count = 0
        if baseline.metadata and hasattr(baseline.metadata, 'document_count'):
            document_count = baseline.metadata.document_count
        elif baseline.source_document_ids:
            document_count = len(baseline.source_document_ids)
        
        return BaselineResponse(
            id=str(baseline.id),
            user_id=baseline.user_id,
            executive_summary=baseline.executive_summary,
            status=baseline.status,
            created_at=baseline.created_at.isoformat(),
            completed_at=baseline.completed_at.isoformat() if baseline.completed_at else None,
            strengths=baseline.strengths or [],
            development_opportunities=baseline.development_opportunities or [],
            key_themes=key_themes,
            development_areas=baseline.development_opportunities or [],  # Alias
            summary=baseline.executive_summary,  # Alias
            document_count=document_count,
            goal_count=0,  # TODO: Implement goal counting if needed
            generated_at=baseline.created_at.isoformat()  # Alias
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error retrieving baseline for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve baseline"
        )