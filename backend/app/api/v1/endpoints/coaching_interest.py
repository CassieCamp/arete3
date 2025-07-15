from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from app.schemas.coaching_interest import CoachingInterestCreate
from app.repositories.coaching_interest_repository import CoachingInterestRepository
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coaching_interest(
    submission: CoachingInterestCreate,
    background_tasks: BackgroundTasks,
    repo: CoachingInterestRepository = Depends(CoachingInterestRepository),
    email_service: EmailService = Depends(EmailService)
):
    """
    Create a new coaching interest submission, saves it to the database,
    and sends a notification email.
    """
    try:
        logger.info(f"Received coaching interest submission: {submission}")
        
        # Save to database
        created_submission = await repo.create(submission)
        
        # Send email notification in the background
        background_tasks.add_task(
            email_service.send_coaching_interest_notification,
            name=submission.name,
            email=submission.email,
            goals=submission.goals
        )
        
        return created_submission
    except Exception as e:
        logger.error(f"Error creating coaching interest: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create coaching interest submission."
        )