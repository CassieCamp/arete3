from fastapi import APIRouter, Request, HTTPException, status
from app.services.user_service import UserService
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/clerk")
async def handle_clerk_webhook(request: Request):
    """Handle Clerk user lifecycle webhooks"""
    try:
        # Get the raw body
        body = await request.body()
        
        # Parse the webhook payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        event_type = payload.get("type")
        data = payload.get("data", {})
        
        logger.info(f"Received Clerk webhook: {event_type}")
        
        user_service = UserService()
        
        if event_type == "user.created":
            # Extract user data from Clerk webhook
            clerk_user_id = data.get("id")
            email_addresses = data.get("email_addresses", [])
            
            if not clerk_user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing user ID in webhook payload"
                )
            
            # Get primary email
            primary_email = None
            for email in email_addresses:
                if email.get("id") == data.get("primary_email_address_id"):
                    primary_email = email.get("email_address")
                    break
            
            if not primary_email and email_addresses:
                primary_email = email_addresses[0].get("email_address")
            
            if not primary_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No email address found in webhook payload"
                )
            
            # Default role - can be updated later via profile creation
            default_role = "client"
            
            # Create user
            await user_service.create_user_from_clerk(
                clerk_user_id=clerk_user_id,
                email=primary_email,
                role=default_role
            )
            
            logger.info(f"Created user from Clerk webhook: {clerk_user_id}")
            
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