from fastapi import APIRouter, Request, HTTPException, status
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.core.config import settings
from app.db.mongodb import get_database
import json
import logging
from svix.webhooks import Webhook

logger = logging.getLogger(__name__)
router = APIRouter()


def verify_webhook_signature(payload: bytes, headers: dict, secret: str) -> bool:
    """Verify Clerk webhook signature using official Svix library"""
    try:
        # Create Svix webhook instance
        wh = Webhook(secret)
        
        # Verify the webhook using Svix
        wh.verify(payload, headers)
        logger.info("Webhook signature verification: VALID")
        return True
    except Exception as e:
        logger.error(f"Webhook signature verification: INVALID - {e}")
        return False


@router.post("/clerk")
async def handle_clerk_webhook(request: Request):
    """Handle Clerk user lifecycle webhooks"""
    logger.info("=== CLERK WEBHOOK RECEIVED ===")
    
    try:
        # Get the raw body and headers
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info(f"Request headers: {headers}")
        logger.info(f"Raw body length: {len(body)} bytes")
        
        # Verify webhook signature if secret is configured
        if hasattr(settings, 'clerk_webhook_secret') and settings.clerk_webhook_secret:
            if not verify_webhook_signature(body, headers, settings.clerk_webhook_secret):
                logger.error("Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature"
                )
        else:
            logger.warning("Webhook signature verification skipped - no secret configured")
        
        # Parse the webhook payload
        try:
            payload = json.loads(body)
            logger.info(f"Parsed payload keys: {list(payload.keys())}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        logger.info(f"Event type: {event_type}")
        logger.info(f"Data keys: {list(data.keys()) if data else 'No data'}")
        
        # Test database connection
        try:
            db = get_database()
            if db is None:
                logger.error("Database connection is None")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database connection failed"
                )
            logger.info("Database connection verified")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
        
        user_service = UserService()
        
        if event_type == "user.created":
            logger.info("Processing user.created event")
            
            # Extract user data from Clerk webhook
            clerk_user_id = data.get("id")
            email_addresses = data.get("email_addresses", [])
            
            logger.info(f"Clerk user ID: {clerk_user_id}")
            logger.info(f"Email addresses count: {len(email_addresses)}")
            logger.info(f"Email addresses data: {email_addresses}")
            
            if not clerk_user_id:
                logger.error("Missing user ID in webhook payload")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing user ID in webhook payload"
                )
            
            # Get primary email
            primary_email = None
            primary_email_id = data.get("primary_email_address_id")
            logger.info(f"Primary email address ID: {primary_email_id}")
            
            for email in email_addresses:
                logger.info(f"Checking email: {email}")
                if email.get("id") == primary_email_id:
                    primary_email = email.get("email_address")
                    logger.info(f"Found primary email: {primary_email}")
                    break
            
            if not primary_email and email_addresses:
                primary_email = email_addresses[0].get("email_address")
                logger.info(f"Using first email as fallback: {primary_email}")
            
            if not primary_email:
                logger.error("No email address found in webhook payload")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No email address found in webhook payload"
                )
            
            # Get role from approved users configuration
            role_service = RoleService()
            assigned_role = role_service.get_role_for_email(primary_email)
            
            # Use assigned role if found, otherwise default to "client"
            final_role = assigned_role if assigned_role else "client"
            
            # Enhanced logging for role assignment
            logger.info(f"=== ROLE ASSIGNMENT PROCESS ===")
            logger.info(f"Email: {primary_email}")
            logger.info(f"Assigned role from config: {assigned_role}")
            logger.info(f"Final role: {final_role}")
            
            if assigned_role:
                logger.info(f"✅ User {primary_email} found in approved users with role: {assigned_role}")
            else:
                logger.info(f"⚠️ User {primary_email} NOT found in approved users, defaulting to: {final_role}")
                logger.info("This user may have signed up without being on the waitlist or approved")
            
            # Create user
            try:
                logger.info(f"Calling user_service.create_user_from_clerk with clerk_user_id={clerk_user_id}, email={primary_email}, role={final_role}")
                created_user = await user_service.create_user_from_clerk(
                    clerk_user_id=clerk_user_id,
                    email=primary_email,
                    role=final_role
                )
                logger.info(f"Successfully created user: {created_user}")
                logger.info(f"User ID: {created_user.id if created_user else 'None'}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                logger.error(f"Exception type: {type(e)}")
                raise
            
            logger.info(f"✅ Successfully created user from Clerk webhook: {clerk_user_id}")
            
        elif event_type == "user.updated":
            # Handle user updates if needed
            clerk_user_id = data.get("id")
            logger.info(f"User updated: {clerk_user_id}")
            
        elif event_type == "user.deleted":
            # Handle user deletion
            clerk_user_id = data.get("id")
            if clerk_user_id:
                await user_service.delete_user(clerk_user_id)
                logger.info(f"Deleted user: {clerk_user_id}")
        
        return {"status": "success", "event_type": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Clerk webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing webhook"
        )