from typing import Optional, List, Dict, Any
from app.models.goal import Goal, ProgressEntry
from app.repositories.goal_repository import GoalRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoalSuggestion:
    """Represents an AI-generated goal suggestion"""
    def __init__(self, goal_statement: str, success_vision: str, source_documents: List[str] = None):
        self.goal_statement = goal_statement
        self.success_vision = success_vision
        self.source_documents = source_documents or []


class GoalService:
    def __init__(self, goal_repository: Optional[GoalRepository] = None):
        """Initialize GoalService with a GoalRepository instance"""
        self.goal_repository = goal_repository or GoalRepository()

    async def create_goal(self, user_id: str, goal_data: dict) -> Goal:
        """Create a new goal for a user using human-centered approach"""
        logger.info(f"=== GoalService.create_goal called ===")
        logger.info(f"Creating goal for user_id: {user_id} with data: {goal_data}")
        
        try:
            # Validate required fields for new structure
            if not goal_data.get("goal_statement"):
                raise ValueError("Goal statement is required")
            if not goal_data.get("success_vision"):
                raise ValueError("Success vision is required")
            
            # Create Goal instance with human-centered structure
            goal = Goal(
                user_id=user_id,
                goal_statement=goal_data["goal_statement"],
                success_vision=goal_data["success_vision"],
                progress_emoji=goal_data.get("progress_emoji", "😐"),
                progress_notes=goal_data.get("progress_notes"),
                ai_suggested=goal_data.get("ai_suggested", False),
                source_documents=goal_data.get("source_documents", []),
                status=goal_data.get("status", "active"),
                tags=goal_data.get("tags", [])
            )
            
            # Add initial progress entry
            initial_progress = ProgressEntry(
                emoji=goal.progress_emoji,
                notes=goal.progress_notes
            )
            goal.progress_history = [initial_progress]
            
            created_goal = await self.goal_repository.create_goal(goal)
            logger.info(f"✅ Successfully created goal with ID: {created_goal.id}")
            
            # Send notification about new goal
            await self._send_goal_notification(created_goal, "created")
            
            return created_goal
            
        except Exception as e:
            logger.error(f"❌ Error creating goal: {e}")
            raise

    async def create_goal_from_suggestion(self, user_id: str, suggestion: GoalSuggestion) -> Goal:
        """Create a goal from an AI suggestion"""
        logger.info(f"=== GoalService.create_goal_from_suggestion called ===")
        logger.info(f"Creating goal from suggestion for user_id: {user_id}")
        
        goal_data = {
            "goal_statement": suggestion.goal_statement,
            "success_vision": suggestion.success_vision,
            "ai_suggested": True,
            "source_documents": suggestion.source_documents,
            "progress_emoji": "😐"  # Neutral starting point
        }
        
        return await self.create_goal(user_id, goal_data)

    async def get_goal(self, goal_id: str, user_id: str) -> Optional[Goal]:
        """Retrieve a specific goal, ensuring the user has permission to view it"""
        logger.info(f"=== GoalService.get_goal called ===")
        logger.info(f"Getting goal_id: {goal_id} for user_id: {user_id}")
        
        try:
            goal = await self.goal_repository.get_goal_by_id(goal_id)
            
            if not goal:
                logger.info(f"Goal {goal_id} not found")
                return None
            
            # Check if user has permission to view this goal
            if goal.user_id != user_id:
                logger.warning(f"User {user_id} attempted to access goal {goal_id} owned by {goal.user_id}")
                raise PermissionError(f"User does not have permission to access this goal")
            
            logger.info(f"✅ Successfully retrieved goal {goal_id}")
            return goal
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting goal: {e}")
            raise

    async def get_all_user_goals(self, user_id: str) -> List[Goal]:
        """Retrieve all goals for a specific user"""
        logger.info(f"=== GoalService.get_all_user_goals called ===")
        logger.info(f"Getting all goals for user_id: {user_id}")
        
        try:
            goals = await self.goal_repository.get_goals_by_user_id(user_id)
            logger.info(f"✅ Successfully retrieved {len(goals)} goals for user {user_id}")
            return goals
            
        except Exception as e:
            logger.error(f"❌ Error getting user goals: {e}")
            raise

    async def update_goal(self, goal_id: str, user_id: str, update_data: dict) -> Optional[Goal]:
        """Update a goal, ensuring the user has permission"""
        logger.info(f"=== GoalService.update_goal called ===")
        logger.info(f"Updating goal_id: {goal_id} for user_id: {user_id} with data: {update_data}")
        
        try:
            # First check if goal exists and user has permission
            existing_goal = await self.get_goal(goal_id, user_id)
            if not existing_goal:
                logger.info(f"Goal {goal_id} not found or user {user_id} has no permission")
                return None
            
            # Validate update data - allow human-centered fields
            allowed_fields = {
                "goal_statement", "success_vision", "progress_emoji", "progress_notes",
                "status", "tags", "source_documents",
                # Legacy fields for backward compatibility
                "title", "description", "priority", "target_date",
                "completion_date", "progress_percentage", "notes"
            }
            
            validated_update_data = {}
            for key, value in update_data.items():
                if key in allowed_fields:
                    validated_update_data[key] = value
                else:
                    logger.warning(f"Ignoring invalid update field: {key}")
            
            if not validated_update_data:
                logger.info("No valid fields to update")
                return existing_goal
            
            # Add updated timestamp
            validated_update_data["updated_at"] = datetime.utcnow()
            
            updated_goal = await self.goal_repository.update_goal(goal_id, validated_update_data)
            
            if updated_goal:
                logger.info(f"✅ Successfully updated goal {goal_id}")
                
                # Send notification if status changed to completed
                if validated_update_data.get("status") == "completed":
                    await self._send_goal_notification(updated_goal, "completed")
                elif "progress_emoji" in validated_update_data or "progress_notes" in validated_update_data:
                    await self._send_goal_notification(updated_goal, "progress_updated")
            else:
                logger.warning(f"Goal {goal_id} was not updated")
            
            return updated_goal
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating goal: {e}")
            raise

    async def update_progress_emotion(self, goal_id: str, user_id: str, emoji: str, notes: Optional[str] = None) -> Optional[Goal]:
        """Update goal progress with emoji and optional notes"""
        logger.info(f"=== GoalService.update_progress_emotion called ===")
        logger.info(f"Updating progress for goal_id: {goal_id}, user_id: {user_id}, emoji: {emoji}")
        
        try:
            # Get existing goal
            existing_goal = await self.get_goal(goal_id, user_id)
            if not existing_goal:
                logger.info(f"Goal {goal_id} not found or user {user_id} has no permission")
                return None
            
            # Create new progress entry
            progress_entry = ProgressEntry(emoji=emoji, notes=notes)
            
            # Update goal with new progress
            update_data = {
                "progress_emoji": emoji,
                "progress_notes": notes,
                "updated_at": datetime.utcnow()
            }
            
            # Add to progress history
            progress_history = existing_goal.progress_history or []
            progress_history.append(progress_entry)
            update_data["progress_history"] = [entry.dict() for entry in progress_history]
            
            updated_goal = await self.goal_repository.update_goal(goal_id, update_data)
            
            if updated_goal:
                logger.info(f"✅ Successfully updated progress for goal {goal_id}")
                
                # Send notification about progress update
                await self._send_goal_notification(updated_goal, "progress_updated")
            else:
                logger.warning(f"Progress update failed for goal {goal_id}")
            
            return updated_goal
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating progress emotion: {e}")
            raise

    async def get_progress_timeline(self, goal_id: str, user_id: str) -> List[ProgressEntry]:
        """Get the progress timeline for a goal"""
        logger.info(f"=== GoalService.get_progress_timeline called ===")
        logger.info(f"Getting progress timeline for goal_id: {goal_id}, user_id: {user_id}")
        
        try:
            goal = await self.get_goal(goal_id, user_id)
            if not goal:
                logger.info(f"Goal {goal_id} not found or user {user_id} has no permission")
                return []
            
            progress_timeline = goal.progress_history or []
            logger.info(f"✅ Retrieved {len(progress_timeline)} progress entries for goal {goal_id}")
            return progress_timeline
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting progress timeline: {e}")
            raise

    async def suggest_goals_from_documents(self, user_id: str, document_ids: List[str]) -> List[GoalSuggestion]:
        """Generate AI-powered goal suggestions based on uploaded documents"""
        logger.info(f"=== GoalService.suggest_goals_from_documents called ===")
        logger.info(f"Generating goal suggestions for user_id: {user_id} from {len(document_ids)} documents")
        
        try:
            # TODO: Implement AI analysis of documents to generate goal suggestions
            # This is a placeholder implementation
            
            # For now, return some example suggestions
            suggestions = [
                GoalSuggestion(
                    goal_statement="Improve communication with my team",
                    success_vision="My team feels heard, we have fewer misunderstandings, and people seem more engaged when I speak",
                    source_documents=document_ids
                ),
                GoalSuggestion(
                    goal_statement="Develop better work-life balance",
                    success_vision="I feel more energized at work and more present at home, with clear boundaries between the two",
                    source_documents=document_ids
                ),
                GoalSuggestion(
                    goal_statement="Build confidence in decision-making",
                    success_vision="I trust my instincts more, make decisions without excessive second-guessing, and feel proud of my choices",
                    source_documents=document_ids
                )
            ]
            
            logger.info(f"✅ Generated {len(suggestions)} goal suggestions for user {user_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating goal suggestions: {e}")
            raise

    async def enhance_success_vision(self, goal_statement: str, user_context: dict) -> List[str]:
        """Provide success vision suggestions based on goal statement and user context"""
        logger.info(f"=== GoalService.enhance_success_vision called ===")
        logger.info(f"Enhancing success vision for goal: {goal_statement}")
        
        try:
            # TODO: Implement AI-powered success vision enhancement
            # This is a placeholder implementation
            
            suggestions = [
                "I feel more confident and comfortable in situations related to this goal",
                "Others notice positive changes in how I approach this area",
                "I experience less stress and more satisfaction when dealing with this topic",
                "I can see clear progress in small, daily interactions and decisions"
            ]
            
            logger.info(f"✅ Generated {len(suggestions)} success vision suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error enhancing success vision: {e}")
            raise

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete a goal, ensuring the user has permission"""
        logger.info(f"=== GoalService.delete_goal called ===")
        logger.info(f"Deleting goal_id: {goal_id} for user_id: {user_id}")
        
        try:
            # First check if goal exists and user has permission
            existing_goal = await self.get_goal(goal_id, user_id)
            if not existing_goal:
                logger.info(f"Goal {goal_id} not found or user {user_id} has no permission")
                return False
            
            success = await self.goal_repository.delete_goal(goal_id)
            
            if success:
                logger.info(f"✅ Successfully deleted goal {goal_id}")
            else:
                logger.warning(f"Goal {goal_id} was not deleted")
            
            return success
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error deleting goal: {e}")
            raise

    async def get_goals_by_status(self, user_id: str, status: str) -> List[Goal]:
        """Get all goals for a user filtered by status"""
        logger.info(f"=== GoalService.get_goals_by_status called ===")
        logger.info(f"Getting goals for user_id: {user_id} with status: {status}")
        
        try:
            all_goals = await self.get_all_user_goals(user_id)
            filtered_goals = [goal for goal in all_goals if goal.status == status]
            
            logger.info(f"✅ Found {len(filtered_goals)} goals with status '{status}' for user {user_id}")
            return filtered_goals
            
        except Exception as e:
            logger.error(f"❌ Error getting goals by status: {e}")
            raise

    async def get_goals_by_priority(self, user_id: str, priority: str) -> List[Goal]:
        """Get all goals for a user filtered by priority"""
        logger.info(f"=== GoalService.get_goals_by_priority called ===")
        logger.info(f"Getting goals for user_id: {user_id} with priority: {priority}")
        
        try:
            all_goals = await self.get_all_user_goals(user_id)
            filtered_goals = [goal for goal in all_goals if goal.priority == priority]
            
            logger.info(f"✅ Found {len(filtered_goals)} goals with priority '{priority}' for user {user_id}")
            return filtered_goals
            
        except Exception as e:
            logger.error(f"❌ Error getting goals by priority: {e}")
            raise
    
    async def _send_goal_notification(self, goal: Goal, update_type: str):
        """Send notification about goal updates"""
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            await notification_service.notify_goal_update(
                user_id=goal.user_id,
                goal_id=str(goal.id),
                goal_title=goal.goal_statement,
                update_type=update_type
            )
            
            logger.info(f"✅ Sent {update_type} notification for goal: {goal.id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending goal notification: {e}")
            # Don't raise the error as the goal operation was successful