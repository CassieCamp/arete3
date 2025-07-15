from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    goals: str
    email_permission: bool

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def submit_contact_form(
    submission: ContactForm,
    background_tasks: BackgroundTasks,
    email_service: EmailService = Depends(EmailService)
):
    """
    Accepts a contact form submission and sends an email notification.
    """
    try:
        logger.info(f"Received contact form submission: {submission.name} <{submission.email}>")
        
        if not submission.email_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email permission is required to submit this form."
            )

        background_tasks.add_task(
            email_service.send_coaching_interest_notification,
            name=submission.name,
            email=submission.email,
            goals=submission.goals
        )
        
        return {"message": "Your submission has been received."}
    except Exception as e:
        logger.error(f"Error processing contact form: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error processing your request."
        )