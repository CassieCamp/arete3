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
            
            # Extract role data from Clerk publicMetadata
            public_metadata = data.get("public_metadata", {})
            primary_role = public_metadata.get("primary_role", "member")
            organization_roles = public_metadata.get("organization_roles", {})
            
            # Enhanced logging for role assignment
            logger.info(f"=== ROLE ASSIGNMENT FROM CLERK METADATA ===")
            logger.info(f"Email: {primary_email}")
            logger.info(f"Public metadata: {public_metadata}")
            logger.info(f"Primary role: {primary_role}")
            logger.info(f"Organization roles: {organization_roles}")
            
            # Create user with Clerk-provided role data
            try:
                logger.info(f"Calling user_service.create_user_from_clerk with clerk_user_id={clerk_user_id}, email={primary_email}, primary_role={primary_role}")
                created_user = await user_service.create_user_from_clerk(
                    clerk_user_id=clerk_user_id,
                    email=primary_email,
                    primary_role=primary_role,
                    organization_roles=organization_roles
                )
                logger.info(f"Successfully created user: {created_user}")
                logger.info(f"User ID: {created_user.id if created_user else 'None'}")
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                logger.error(f"Exception type: {type(e)}")
                raise
            
            logger.info(f"✅ Successfully created user from Clerk webhook: {clerk_user_id}")
            
        elif event_type == "user.updated":
            # Handle user updates - sync role changes from Clerk and invalidate sessions if role changed
            clerk_user_id = data.get("id")
            logger.info(f"Processing user.updated event for: {clerk_user_id}")
            
            # Extract updated role data from Clerk publicMetadata
            public_metadata = data.get("public_metadata", {})
            
            if public_metadata:
                primary_role = public_metadata.get("primary_role")
                organization_roles = public_metadata.get("organization_roles", {})
                
                logger.info(f"=== ROLE UPDATE FROM CLERK METADATA ===")
                logger.info(f"Clerk user ID: {clerk_user_id}")
                logger.info(f"Updated public metadata: {public_metadata}")
                logger.info(f"Updated primary role: {primary_role}")
                logger.info(f"Updated organization roles: {organization_roles}")
                
                try:
                    # Get current user to check if role actually changed
                    current_user = await user_service.get_user_by_clerk_id(clerk_user_id)
                    role_changed = False
                    
                    if current_user and hasattr(current_user, 'primary_role'):
                        old_role = getattr(current_user, 'primary_role', None)
                        if old_role != primary_role:
                            role_changed = True
                            logger.info(f"🔄 Role change detected: {old_role} -> {primary_role}")
                    
                    # Update user role data from Clerk
                    updated_user = await user_service.update_user_role_from_clerk(
                        clerk_user_id=clerk_user_id,
                        primary_role=primary_role,
                        organization_roles=organization_roles
                    )
                    
                    if updated_user:
                        logger.info(f"✅ Successfully updated user roles: {clerk_user_id}")
                        
                        # If primary role changed, refresh user sessions
                        if role_changed and primary_role:
                            logger.info(f"🔄 Primary role changed, refreshing sessions for user: {clerk_user_id}")
                            try:
                                # Import Clerk client for session refresh
                                from app.core.config import settings
                                from clerk_backend_api import Clerk
                                
                                clerk_client = Clerk(bearer_auth=settings.clerk_secret_key)
                                
                                # Get all active sessions for the user
                                sessions = clerk_client.users.get_user_sessions(user_id=clerk_user_id)
                                logger.info(f"📱 Found {len(sessions)} active sessions for user {clerk_user_id}")
                                
                                # Revoke all active sessions to force refresh
                                revoked_count = 0
                                for session in sessions:
                                    try:
                                        clerk_client.sessions.revoke_session(session_id=session.id)
                                        revoked_count += 1
                                        logger.info(f"🔄 Revoked session {session.id}")
                                    except Exception as revoke_error:
                                        logger.warning(f"⚠️ Failed to revoke session {session.id}: {revoke_error}")
                                
                                logger.info(f"✅ Successfully revoked {revoked_count} sessions for user {clerk_user_id} - role change will take effect on next sign-in")
                                
                            except Exception as session_error:
                                logger.error(f"❌ Failed to refresh sessions for {clerk_user_id}: {session_error}")
                                # Fallback to ban/unban approach
                                try:
                                    logger.info(f"🔄 Falling back to ban/unban approach for {clerk_user_id}")
                                    clerk_client.users.ban(user_id=clerk_user_id)
                                    import time
                                    time.sleep(1)
                                    clerk_client.users.unban(user_id=clerk_user_id)
                                    logger.info(f"✅ Fallback session invalidation completed for {clerk_user_id}")
                                except Exception as fallback_error:
                                    logger.error(f"❌ Fallback session invalidation failed for {clerk_user_id}: {fallback_error}")
                    else:
                        logger.warning(f"⚠️ User not found for role update: {clerk_user_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error updating user roles: {e}")
            else:
                logger.info(f"No publicMetadata changes for user: {clerk_user_id}")
            
        elif event_type == "user.deleted":
            # Handle user deletion
            clerk_user_id = data.get("id")
            if clerk_user_id:
                await user_service.delete_user(clerk_user_id)
                logger.info(f"Deleted user: {clerk_user_id}")
        
        elif event_type == "organizationMembership.created":
            # Handle new organization membership
            logger.info("Processing organizationMembership.created event")
            
            user_id = data.get("public_user_data", {}).get("user_id")
            org_id = data.get("organization", {}).get("id")
            role = data.get("role", "basic_member")
            
            if user_id and org_id:
                # Get organization details to determine type
                try:
                    org_details = await clerk_org_service.get_organization_with_metadata(org_id)
                    org_type = org_details.get("metadata", {}).get("organization_type", "unknown") if org_details else "unknown"
                    
                    # Add organization membership to user
                    success = await user_service.add_organization_membership(user_id, org_id, role, org_type)
                    
                    if success:
                        logger.info(f"✅ Added organization membership: user {user_id} to org {org_id} with role {role}")
                    else:
                        logger.warning(f"⚠️ Failed to add organization membership: user {user_id} to org {org_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing organization membership creation: {e}")
            else:
                logger.warning("Missing user_id or org_id in organizationMembership.created event")
        
        elif event_type == "organizationMembership.updated":
            # Handle organization membership role changes
            logger.info("Processing organizationMembership.updated event")
            
            user_id = data.get("public_user_data", {}).get("user_id")
            org_id = data.get("organization", {}).get("id")
            new_role = data.get("role", "basic_member")
            
            if user_id and org_id:
                try:
                    success = await user_service.update_user_role_in_organization(user_id, org_id, new_role)
                    
                    if success:
                        logger.info(f"✅ Updated organization role: user {user_id} in org {org_id} to role {new_role}")
                    else:
                        logger.warning(f"⚠️ Failed to update organization role: user {user_id} in org {org_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing organization membership update: {e}")
            else:
                logger.warning("Missing user_id or org_id in organizationMembership.updated event")
        
        elif event_type == "organizationMembership.deleted":
            # Handle organization membership removal
            logger.info("Processing organizationMembership.deleted event")
            
            user_id = data.get("public_user_data", {}).get("user_id")
            org_id = data.get("organization", {}).get("id")
            
            if user_id and org_id:
                try:
                    success = await user_service.remove_organization_membership(user_id, org_id)
                    
                    if success:
                        logger.info(f"✅ Removed organization membership: user {user_id} from org {org_id}")
                    else:
                        logger.warning(f"⚠️ Failed to remove organization membership: user {user_id} from org {org_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing organization membership deletion: {e}")
            else:
                logger.warning("Missing user_id or org_id in organizationMembership.deleted event")
        
        elif event_type == "organization.created":
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