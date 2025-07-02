from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
from datetime import datetime
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

router = APIRouter()
logger = logging.getLogger(__name__)

class DiscoveryFormSubmission(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    linkedinUrl: Optional[str] = None
    roles: List[str]
    feedback: Optional[str] = None
    timestamp: str

def send_email_notification(form_data: DiscoveryFormSubmission):
    """Send email notification using SendGrid"""
    try:
        # Get SendGrid API key from environment variable
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not sendgrid_api_key:
            logger.error("SENDGRID_API_KEY environment variable not set")
            return False
        
        # Email configuration
        from_email = "cassie@cassiecamp.com"  # Verified sender in SendGrid
        to_email = "cassie@cassiecamp.com"
        
        # Format the email content
        roles_text = ", ".join(form_data.roles) if form_data.roles else "None selected"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1B1E3C; border-bottom: 2px solid #D6B370; padding-bottom: 10px;">
                    New Discovery Form Submission
                </h2>
                
                <div style="background-color: #f8f7f2; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1B1E3C; margin-top: 0;">Contact Information</h3>
                    <p><strong>Name:</strong> {form_data.firstName} {form_data.lastName}</p>
                    <p><strong>Email:</strong> <a href="mailto:{form_data.email}">{form_data.email}</a></p>
                    <p><strong>LinkedIn:</strong> {form_data.linkedinUrl or "Not provided"}</p>
                    <p><strong>Submitted:</strong> {form_data.timestamp}</p>
                </div>
                
                <div style="background-color: #f8f7f2; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1B1E3C; margin-top: 0;">Role(s)</h3>
                    <p>{roles_text}</p>
                </div>
                
                <div style="background-color: #f8f7f2; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1B1E3C; margin-top: 0;">Feedback</h3>
                    <p style="font-style: italic;">{form_data.feedback or "No feedback provided"}</p>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666;">
                    <p>This email was automatically generated from the Arete discovery form.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create the email message
        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=f"🔔 New Discovery Form Submission - {form_data.firstName} {form_data.lastName}",
            html_content=html_content
        )
        
        # Send the email
        sg = SendGridAPIClient(api_key=sendgrid_api_key)
        response = sg.send(message)
        
        logger.info(f"Email sent successfully to {to_email}")
        logger.info(f"SendGrid response status: {response.status_code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email notification via SendGrid: {str(e)}")
        return False

@router.post("/submit")
async def submit_discovery_form(
    form_data: DiscoveryFormSubmission,
    background_tasks: BackgroundTasks
):
    """Handle discovery form submission and send email notification"""
    try:
        # Log the submission
        logger.info(f"Discovery form submitted by {form_data.firstName} {form_data.lastName}")
        
        # Add email notification to background tasks
        background_tasks.add_task(send_email_notification, form_data)
        
        # Here you could also save to database if needed
        # await save_to_database(form_data)
        
        return {
            "success": True,
            "message": "Form submitted successfully",
            "data": form_data.dict()
        }
        
    except Exception as e:
        logger.error(f"Error processing discovery form submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")