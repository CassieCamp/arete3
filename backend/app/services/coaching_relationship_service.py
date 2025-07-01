from typing import Optional
from app.models.coaching_relationship import CoachingRelationship, RelationshipStatus
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)


class CoachingRelationshipService:
    def __init__(self, coaching_relationship_repository: CoachingRelationshipRepository, user_repository: UserRepository):
        """Initialize the service with repository dependencies"""
        self.coaching_relationship_repository = coaching_relationship_repository
        self.user_repository = user_repository

    async def create_connection_request(self, coach_user_id: str, client_email: str) -> CoachingRelationship:
        """
        Create a new connection request initiated by a coach
        
        Args:
            coach_user_id: ID of the coach making the request
            client_email: Email of the client being invited
            
        Returns:
            CoachingRelationship: The created relationship record
            
        Raises:
            ValueError: If client not found, coach not valid, or relationship already exists
        """
        logger.info(f"=== CoachingRelationshipService.create_connection_request called ===")
        logger.info(f"Coach user ID: {coach_user_id}, Client email: {client_email}")
        
        try:
            # Verify the coach user exists and has coach role
            coach_user = await self.user_repository.get_user_by_clerk_id(coach_user_id)
            if not coach_user:
                logger.error(f"Coach user not found with ID: {coach_user_id}")
                raise ValueError(f"Coach user with ID {coach_user_id} not found")
            
            if not hasattr(coach_user, 'role') or coach_user.role != 'coach':
                logger.error(f"User {coach_user_id} is not a coach")
                raise ValueError("Only coaches can initiate connection requests")
            
            logger.info(f"Found coach user: {coach_user.id}")
            
            # Find the client user by email
            client_user = await self.user_repository.get_user_by_email(client_email)
            if not client_user:
                logger.error(f"Client user not found with email: {client_email}")
                raise ValueError(f"User with email {client_email} not found")
            
            logger.info(f"Found client user: {client_user.id}")
            
            # Check if a relationship already exists between these users
            existing_relationship = await self.coaching_relationship_repository.get_relationship_between_users(
                coach_user_id, client_user.clerk_user_id
            )
            
            if existing_relationship:
                logger.error(f"Relationship already exists between users: {existing_relationship.id}")
                raise ValueError("A relationship already exists between these users")
            
            # Create new coaching relationship with pending_by_coach status
            new_relationship = CoachingRelationship(
                coach_user_id=coach_user_id,
                client_user_id=client_user.clerk_user_id,
                status=RelationshipStatus.PENDING_BY_COACH
            )
            
            logger.info(f"Creating new relationship: {new_relationship}")
            
            # Save the relationship
            created_relationship = await self.coaching_relationship_repository.create_relationship(new_relationship)
            
            logger.info(f"✅ Successfully created connection request with ID: {created_relationship.id}")
            
            # Send notification to client about the new request
            await self._send_relationship_notification(
                created_relationship, "request_received", client_user.clerk_user_id, coach_user.email
            )
            
            return created_relationship
            
        except Exception as e:
            logger.error(f"❌ Error in create_connection_request: {e}")
            raise

    async def respond_to_connection_request(self, relationship_id: str, responding_user_id: str, new_status: RelationshipStatus) -> CoachingRelationship:
        """
        Respond to a connection request by updating its status
        Only the client can accept or decline a coach-initiated request
        
        Args:
            relationship_id: ID of the relationship to update
            responding_user_id: ID of the user responding to the request (must be the client)
            new_status: New status for the relationship (ACTIVE or DECLINED)
            
        Returns:
            CoachingRelationship: The updated relationship record
            
        Raises:
            ValueError: If relationship not found, user not authorized, or invalid status
        """
        logger.info(f"=== CoachingRelationshipService.respond_to_connection_request called ===")
        logger.info(f"Relationship ID: {relationship_id}, Responding user: {responding_user_id}, New status: {new_status}")
        
        try:
            # Find the relationship by ID
            relationship = await self.coaching_relationship_repository.get_relationship_by_id(relationship_id)
            if not relationship:
                logger.error(f"Relationship not found with ID: {relationship_id}")
                raise ValueError(f"Relationship with ID {relationship_id} not found")
            
            logger.info(f"Found relationship: {relationship}")
            
            # Verify that the responding user is the client (only clients can respond to coach requests)
            if responding_user_id != relationship.client_user_id:
                logger.error(f"User {responding_user_id} is not the client for relationship {relationship_id}")
                raise ValueError("Only the client can respond to a coaching connection request")
            
            # Verify that the relationship is in pending_by_coach status
            if relationship.status != RelationshipStatus.PENDING_BY_COACH:
                logger.error(f"Relationship {relationship_id} is not in pending_by_coach status: {relationship.status}")
                raise ValueError(f"Cannot respond to a request that is already {relationship.status.value}")
            
            # Validate the new status
            if new_status not in [RelationshipStatus.ACTIVE, RelationshipStatus.DECLINED]:
                logger.error(f"Invalid status for response: {new_status}")
                raise ValueError("Response status must be either 'active' or 'declined'")
            
            logger.info(f"Updating relationship status to: {new_status}")
            
            # Update the relationship status
            updated_relationship = await self.coaching_relationship_repository.update_relationship_status(
                relationship_id, new_status
            )
            
            if not updated_relationship:
                logger.error(f"Failed to update relationship {relationship_id}")
                raise ValueError("Failed to update relationship status")
            
            logger.info(f"✅ Successfully updated relationship status to {new_status}")
            
            # Send notification to coach about the response
            if new_status == RelationshipStatus.ACTIVE:
                await self._send_relationship_notification(
                    updated_relationship, "request_accepted", updated_relationship.coach_user_id, "Client"
                )
            elif new_status == RelationshipStatus.DECLINED:
                await self._send_relationship_notification(
                    updated_relationship, "request_declined", updated_relationship.coach_user_id, "Client"
                )
            
            return updated_relationship
            
        except Exception as e:
            logger.error(f"❌ Error in respond_to_connection_request: {e}")
            raise

    async def get_user_relationships(self, user_id: str) -> dict:
        """
        Get all relationships for a user (both pending and active)
        
        Args:
            user_id: ID of the user to get relationships for
            
        Returns:
            dict: Dictionary containing pending and active relationships
        """
        logger.info(f"=== CoachingRelationshipService.get_user_relationships called ===")
        logger.info(f"Getting relationships for user_id: {user_id}")
        
        try:
            # Get pending requests
            pending_relationships = await self.coaching_relationship_repository.get_pending_requests_for_user(user_id)
            
            # Get active relationships
            active_relationships = await self.coaching_relationship_repository.get_active_relationships_for_user(user_id)
            
            logger.info(f"✅ Found {len(pending_relationships)} pending and {len(active_relationships)} active relationships")
            
            return {
                "pending": pending_relationships,
                "active": active_relationships
            }
            
        except Exception as e:
            logger.error(f"❌ Error in get_user_relationships: {e}")
            raise
    
    async def _send_relationship_notification(self, relationship: CoachingRelationship, update_type: str, recipient_user_id: str, other_user_name: str):
        """Send notification about coaching relationship updates"""
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            await notification_service.notify_coaching_relationship_update(
                user_id=recipient_user_id,
                relationship_id=str(relationship.id),
                update_type=update_type,
                other_user_name=other_user_name
            )
            
            logger.info(f"✅ Sent {update_type} notification for relationship: {relationship.id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending relationship notification: {e}")
            # Don't raise the error as the relationship operation was successful