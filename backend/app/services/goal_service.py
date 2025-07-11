from typing import Optional, List, Dict, Any
from app.models.goal import Goal, ProgressEntry
from app.repositories.goal_repository import GoalRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoalSuggestion:
    """Represents an AI-generated goal suggestion (backward compatibility)"""
    def __init__(self, goal_statement: str, success_vision: str, source_documents: List[str] = None):
        self.goal_statement = goal_statement
        self.success_vision = success_vision
        self.source_documents = source_documents or []


class GoalService:
    """
    Backward compatibility wrapper that delegates to DestinationService.
    This service no longer imports DestinationService directly to avoid circular dependencies.
    Instead, it imports DestinationService dynamically when needed.
    """
    def __init__(self, goal_repository: Optional[GoalRepository] = None):
        """Initialize GoalService with backward compatibility"""
        logger.info("GoalService initialized with backward compatibility to DestinationService")
        self.goal_repository = goal_repository or GoalRepository()

    def _get_destination_service(self):
        """Get DestinationService instance dynamically to avoid circular imports"""
        from app.services.destination_service import DestinationService
        return DestinationService()

    async def create_goal(self, user_id: str, goal_data: dict) -> Goal:
        """Create a new goal for a user (backward compatibility wrapper)"""
        logger.info(f"=== GoalService.create_goal called (backward compatibility) ===")
        logger.info(f"Delegating to DestinationService for user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            
            # Convert goal_statement to destination_statement for new service
            destination_data = goal_data.copy()
            if "goal_statement" in destination_data:
                destination_data["destination_statement"] = destination_data.pop("goal_statement")
            
            # Create destination using new service
            destination = await destination_service.create_destination(user_id, destination_data)
            
            # Convert destination back to goal format for backward compatibility
            goal = destination_service._destination_to_goal(destination)
            
            logger.info(f"✅ Successfully created goal via DestinationService with ID: {goal.id}")
            return goal
            
        except Exception as e:
            logger.error(f"❌ Error creating goal: {e}")
            raise

    async def create_goal_from_suggestion(self, user_id: str, suggestion: GoalSuggestion) -> Goal:
        """Create a goal from an AI suggestion"""
        logger.info(f"=== GoalService.create_goal_from_suggestion called ===")
        logger.info(f"Creating goal from suggestion for user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.create_goal_from_suggestion(user_id, suggestion)
        except Exception as e:
            logger.error(f"❌ Error creating goal from suggestion: {e}")
            raise

    async def get_goal(self, goal_id: str, user_id: str) -> Optional[Goal]:
        """Retrieve a specific goal, ensuring the user has permission to view it"""
        logger.info(f"=== GoalService.get_goal called ===")
        logger.info(f"Getting goal_id: {goal_id} for user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.get_goal_wrapper(goal_id, user_id)
        except Exception as e:
            logger.error(f"❌ Error getting goal: {e}")
            raise

    async def get_all_user_goals(self, user_id: str) -> List[Goal]:
        """Retrieve all goals for a specific user"""
        logger.info(f"=== GoalService.get_all_user_goals called ===")
        logger.info(f"Getting all goals for user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.get_all_user_goals_wrapper(user_id)
        except Exception as e:
            logger.error(f"❌ Error getting user goals: {e}")
            raise

    async def update_goal(self, goal_id: str, user_id: str, update_data: dict) -> Optional[Goal]:
        """Update a goal, ensuring the user has permission"""
        logger.info(f"=== GoalService.update_goal called ===")
        logger.info(f"Updating goal_id: {goal_id} for user_id: {user_id} with data: {update_data}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.update_goal_wrapper(goal_id, user_id, update_data)
        except Exception as e:
            logger.error(f"❌ Error updating goal: {e}")
            raise

    async def update_progress_emotion(self, goal_id: str, user_id: str, emoji: str, notes: Optional[str] = None) -> Optional[Goal]:
        """Update goal progress with emoji and optional notes"""
        logger.info(f"=== GoalService.update_progress_emotion called ===")
        logger.info(f"Updating progress for goal_id: {goal_id}, user_id: {user_id}, emoji: {emoji}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.update_progress_emotion_wrapper(goal_id, user_id, emoji, notes)
        except Exception as e:
            logger.error(f"❌ Error updating progress emotion: {e}")
            raise

    async def get_progress_timeline(self, goal_id: str, user_id: str) -> List[ProgressEntry]:
        """Get the progress timeline for a goal"""
        logger.info(f"=== GoalService.get_progress_timeline called ===")
        logger.info(f"Getting progress timeline for goal_id: {goal_id}, user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.get_progress_timeline_wrapper(goal_id, user_id)
        except Exception as e:
            logger.error(f"❌ Error getting progress timeline: {e}")
            raise

    async def suggest_goals_from_documents(self, user_id: str, document_ids: List[str]) -> List[GoalSuggestion]:
        """Generate AI-powered goal suggestions based on uploaded documents"""
        logger.info(f"=== GoalService.suggest_goals_from_documents called ===")
        logger.info(f"Generating goal suggestions for user_id: {user_id} from {len(document_ids)} documents")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.suggest_goals_from_documents(user_id, document_ids)
        except Exception as e:
            logger.error(f"❌ Error generating goal suggestions: {e}")
            raise

    async def enhance_success_vision(self, goal_statement: str, user_context: dict) -> List[str]:
        """Provide success vision suggestions based on goal statement and user context"""
        logger.info(f"=== GoalService.enhance_success_vision called ===")
        logger.info(f"Enhancing success vision for goal: {goal_statement}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.enhance_success_vision(goal_statement, user_context)
        except Exception as e:
            logger.error(f"❌ Error enhancing success vision: {e}")
            raise

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal, ensuring the user has permission"""
        logger.info(f"=== GoalService.delete_goal called ===")
        logger.info(f"Deleting goal_id: {goal_id} for user_id: {user_id}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.delete_goal_wrapper(goal_id, user_id)
        except Exception as e:
            logger.error(f"❌ Error deleting goal: {e}")
            raise

    async def get_goals_by_status(self, user_id: str, status: str) -> List[Goal]:
        """Get all goals for a user filtered by status"""
        logger.info(f"=== GoalService.get_goals_by_status called ===")
        logger.info(f"Getting goals for user_id: {user_id} with status: {status}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.get_goals_by_status_wrapper(user_id, status)
        except Exception as e:
            logger.error(f"❌ Error getting goals by status: {e}")
            raise

    async def get_goals_by_priority(self, user_id: str, priority: str) -> List[Goal]:
        """Get all goals for a user filtered by priority"""
        logger.info(f"=== GoalService.get_goals_by_priority called ===")
        logger.info(f"Getting goals for user_id: {user_id} with priority: {priority}")
        
        try:
            destination_service = self._get_destination_service()
            return await destination_service.get_goals_by_priority_wrapper(user_id, priority)
        except Exception as e:
            logger.error(f"❌ Error getting goals by priority: {e}")
            raise

    async def _send_goal_notification(self, goal: Goal, update_type: str):
        """Send notification about goal updates (deprecated - kept for compatibility)"""
        logger.info(f"Goal notification method called (deprecated): {update_type} for goal {goal.id}")
        # This method is kept for any existing code that might call it directly
        # The actual notifications are now handled by DestinationService