from fastapi import APIRouter, Request, HTTPException, status
from app.services.user_service import UserService
from app.services.clerk_organization_service import ClerkOrganizationService
from app.core.config import settings
from app.db.mongodb import get_database
import json
import logging
from svix.webhooks import Webhook
from datetime import datetime

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
        clerk_org_service = ClerkOrganizationService()
        
        if event_type == "organization.created":
            # Handle new organization creation
            logger.info("Processing organization.created event")
            
            org_id = data.get("id")
            org_name = data.get("name")
            created_by = data.get("created_by")
            
            logger.info(f"New organization created: {org_name} (ID: {org_id}) by user {created_by}")
            # Additional organization setup logic can be added here if needed
        
        elif event_type == "organization.updated":
            # Handle organization updates
            logger.info("Processing organization.updated event")
            
            org_id = data.get("id")
            org_name = data.get("name")
            
            logger.info(f"Organization updated: {org_name} (ID: {org_id})")
            # Additional organization update logic can be added here if needed
        
        elif event_type == "organization.deleted":
            # Handle organization deletion
            logger.info("Processing organization.deleted event")
            
            org_id = data.get("id")
            org_name = data.get("name")
            
            logger.info(f"Organization deleted: {org_name} (ID: {org_id})")
            # Additional cleanup logic can be added here if needed
        
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {"status": "success", "event_type": event_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Clerk webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing webhook"
        )