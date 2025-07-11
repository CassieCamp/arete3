from typing import Dict, Any, Optional
from app.repositories.profile_repository import ProfileRepository
from app.repositories.entry_repository import EntryRepository
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
import logging

logger = logging.getLogger(__name__)


class FreemiumService:
    def __init__(self):
        self.profiles_repository = ProfileRepository()
        self.entries_repository = EntryRepository()
        self.coaching_relationships_repository = CoachingRelationshipRepository()

    async def get_freemium_status(self, user_id: str) -> Dict[str, Any]:
        """
        Check and return the freemium status for a user.
        Determines if user has a coach and their entry count limits.
        """
        try:
            logger.info(f"=== FreemiumService.get_freemium_status called ===")
            logger.info(f"Checking freemium status for user_id: {user_id}")
            
            # Get user profile
            profile = await self.profiles_repository.get_profile_by_clerk_id(user_id)
            if not profile:
                raise ValueError("User profile not found")
            
            # Check if user has an active coaching relationship
            has_coach = await self._check_has_active_coach(user_id)
            
            # Get current entry count
            entries_count = await self.entries_repository.get_entries_count_by_user(user_id)
            
            # Get freemium settings from profile or use defaults
            freemium_status = profile.freemium_status
            if not freemium_status:
                # Initialize default freemium status
                freemium_status = {
                    "has_coach": has_coach,
                    "entries_count": entries_count,
                    "max_free_entries": 3,
                    "coach_requested": False,
                    "coach_request_date": None
                }
                
                # Update profile with initial freemium status
                await self._update_profile_freemium_status(user_id, freemium_status)
            else:
                # Update current status
                freemium_status = freemium_status.model_dump() if hasattr(freemium_status, 'model_dump') else freemium_status
                freemium_status["has_coach"] = has_coach
                freemium_status["entries_count"] = entries_count
            
            # Determine access levels
            can_create_entries = has_coach or entries_count < freemium_status.get("max_free_entries", 3)
            can_access_insights = has_coach
            can_access_destinations = has_coach or entries_count > 0
            
            result = {
                **freemium_status,
                "can_create_entries": can_create_entries,
                "can_access_insights": can_access_insights,
                "can_access_destinations": can_access_destinations,
                "is_freemium": not has_coach,
                "entries_remaining": max(0, freemium_status.get("max_free_entries", 3) - entries_count) if not has_coach else None
            }
            
            logger.info(f"✅ Successfully retrieved freemium status for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting freemium status: {e}")
            raise

    async def can_create_entry(self, user_id: str) -> bool:
        """
        Check if user can create a new entry based on freemium limits.
        """
        try:
            logger.info(f"=== FreemiumService.can_create_entry called ===")
            logger.info(f"Checking entry creation permission for user_id: {user_id}")
            
            freemium_status = await self.get_freemium_status(user_id)
            can_create = freemium_status.get("can_create_entries", False)
            
            logger.info(f"✅ User {user_id} can create entry: {can_create}")
            return can_create
            
        except Exception as e:
            logger.error(f"❌ Error checking entry creation permission: {e}")
            return False  # Default to not allowing

    async def increment_entry_count(self, user_id: str) -> bool:
        """
        Increment the entry count for freemium users.
        This should be called after successfully creating an entry.
        """
        try:
            logger.info(f"=== FreemiumService.increment_entry_count called ===")
            logger.info(f"Incrementing entry count for user_id: {user_id}")
            
            # Get current status
            freemium_status = await self.get_freemium_status(user_id)
            
            # Only increment for freemium users
            if freemium_status.get("is_freemium", True):
                new_count = freemium_status.get("entries_count", 0) + 1
                
                # Update the profile
                updated_status = freemium_status.copy()
                updated_status["entries_count"] = new_count
                
                success = await self._update_profile_freemium_status(user_id, updated_status)
                
                if success:
                    logger.info(f"✅ Successfully incremented entry count to {new_count} for user {user_id}")
                else:
                    logger.warning(f"Failed to increment entry count for user {user_id}")
                
                return success
            else:
                logger.info(f"User {user_id} has coach, no need to increment entry count")
                return True
            
        except Exception as e:
            logger.error(f"❌ Error incrementing entry count: {e}")
            return False

    async def request_coach(self, user_id: str) -> bool:
        """
        Mark that a freemium user has requested a coach.
        """
        try:
            logger.info(f"=== FreemiumService.request_coach called ===")
            logger.info(f"Processing coach request for user_id: {user_id}")
            
            # Get current status
            freemium_status = await self.get_freemium_status(user_id)
            
            # Update coach request status
            from datetime import datetime
            updated_status = freemium_status.copy()
            updated_status["coach_requested"] = True
            updated_status["coach_request_date"] = datetime.utcnow()
            
            success = await self._update_profile_freemium_status(user_id, updated_status)
            
            if success:
                logger.info(f"✅ Successfully marked coach request for user {user_id}")
                
                # Send notification to admins about coach request
                await self._notify_coach_request(user_id)
            else:
                logger.warning(f"Failed to mark coach request for user {user_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error processing coach request: {e}")
            return False

    async def upgrade_from_freemium(self, user_id: str, coaching_relationship_id: str) -> bool:
        """
        Upgrade a user from freemium when they get a coach.
        """
        try:
            logger.info(f"=== FreemiumService.upgrade_from_freemium called ===")
            logger.info(f"Upgrading user {user_id} from freemium")
            
            # Get current status
            freemium_status = await self.get_freemium_status(user_id)
            
            # Update status to reflect coach assignment
            from datetime import datetime
            updated_status = freemium_status.copy()
            updated_status["has_coach"] = True
            updated_status["coach_assigned_date"] = datetime.utcnow()
            
            # Update profile
            success = await self._update_profile_freemium_status(user_id, updated_status)
            
            if success:
                # Also update the coaching relationship to mark freemium upgrade
                await self.coaching_relationships_repository.update_relationship(
                    coaching_relationship_id,
                    {
                        "upgraded_from_freemium": True,
                        "upgrade_date": datetime.utcnow()
                    }
                )
                
                logger.info(f"✅ Successfully upgraded user {user_id} from freemium")
            else:
                logger.warning(f"Failed to upgrade user {user_id} from freemium")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error upgrading from freemium: {e}")
            return False

    async def get_freemium_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about freemium users (admin function).
        """
        try:
            logger.info(f"=== FreemiumService.get_freemium_analytics called ===")
            
            # This would require additional repository methods to aggregate data
            # For now, return placeholder analytics
            analytics = {
                "total_freemium_users": 0,
                "users_with_coaches": 0,
                "coach_requests_pending": 0,
                "average_entries_per_freemium_user": 0,
                "conversion_rate": 0,
                "freemium_user_activity": {
                    "active_last_7_days": 0,
                    "active_last_30_days": 0
                }
            }
            
            logger.info(f"✅ Successfully retrieved freemium analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting freemium analytics: {e}")
            raise

    async def _check_has_active_coach(self, user_id: str) -> bool:
        """
        Check if user has an active coaching relationship.
        """
        try:
            # Get all relationships where user is a client
            relationships = await self.coaching_relationships_repository.get_active_relationships_for_user(user_id)
            
            # Check if any are active
            for relationship in relationships:
                if relationship.status == "active":
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking active coach status: {e}")
            return False

    async def _update_profile_freemium_status(self, user_id: str, freemium_status: Dict[str, Any]) -> bool:
        """
        Update the freemium status in the user's profile.
        """
        try:
            # Get profile
            profile = await self.profiles_repository.get_profile_by_clerk_id(user_id)
            if not profile:
                return False
            
            # Update freemium status
            from app.models.profile import FreemiumStatus
            from datetime import datetime
            
            # Convert dict to FreemiumStatus model
            freemium_model = FreemiumStatus(**freemium_status)
            
            # Update profile
            success = await self.profiles_repository.update_profile(
                str(profile.id),
                {
                    "freemium_status": freemium_model.model_dump(),
                    "updated_at": datetime.utcnow()
                }
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error updating profile freemium status: {e}")
            return False

    async def _notify_coach_request(self, user_id: str):
        """
        Send notification to admins about a coach request.
        """
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            # This would send notifications to admin users
            # Implementation depends on notification system
            logger.info(f"Coach request notification sent for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending coach request notification: {e}")
            # Don't raise as this is not critical