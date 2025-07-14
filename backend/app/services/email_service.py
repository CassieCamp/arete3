import logging
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.sendgrid_client = None
        if settings.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(api_key=settings.sendgrid_api_key)
        else:
            logger.warning("SendGrid API key not configured")

    async def send_coaching_interest_notification(self, name: str, email: str, goals: str) -> bool:
        """
        Send coaching interest notification email to cassie@cassiecamp.com
        
        Args:
            name: Name of the person interested in coaching
            email: Email of the person interested in coaching
            goals: Goals/description provided by the person
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self.sendgrid_client:
            logger.error("SendGrid client not initialized - API key missing")
            return False
        
        try:
            # Create email content
            subject = f"New Coaching Interest: {name}"
            
            html_content = f"""
            <html>
            <body>
                <h2>New Coaching Interest Submission</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Goals:</strong></p>
                <p>{goals.replace(chr(10), '<br>')}</p>
                <hr>
                <p><em>This person has granted permission to be contacted via email.</em></p>
            </body>
            </html>
            """
            
            plain_text_content = f"""
            New Coaching Interest Submission
            
            Name: {name}
            Email: {email}
            Goals: {goals}
            
            ---
            This person has granted permission to be contacted via email.
            """
            
            # Create the email message
            message = Mail(
                from_email='noreply@cassiecamp.com',
                to_emails='cassie@cassiecamp.com',
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_text_content
            )
            
            # Send the email
            logger.info(f"Sending coaching interest notification for {name} ({email})")
            response = self.sendgrid_client.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"✅ Successfully sent coaching interest notification for {name}")
                return True
            else:
                logger.error(f"❌ Failed to send email. Status code: {response.status_code}")
                logger.error(f"Response body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error sending coaching interest notification: {e}")
            return False