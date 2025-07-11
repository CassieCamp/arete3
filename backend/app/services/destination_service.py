from typing import Optional, List, Dict, Any
from app.models.destination import Destination, ProgressEntry
from app.repositories.destination_repository import DestinationRepository
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GoalSuggestion:
    """Represents an AI-generated goal suggestion (backward compatibility)"""
    def __init__(self, goal_statement: str, success_vision: str, source_documents: List[str] = None):
        self.goal_statement = goal_statement
        self.success_vision = success_vision
        self.source_documents = source_documents or []


class DestinationSuggestion:
    """Represents an AI-generated destination suggestion"""
    def __init__(self, destination_statement: str, success_vision: str, source_documents: List[str] = None, source_entries: List[str] = None):
        self.destination_statement = destination_statement
        self.success_vision = success_vision
        self.source_documents = source_documents or []
        self.source_entries = source_entries or []


class DestinationService:
    def __init__(self, destination_repository: Optional[DestinationRepository] = None):
        """Initialize DestinationService with a DestinationRepository instance"""
        self.destination_repository = destination_repository or DestinationRepository()

    async def create_destination(self, user_id: str, destination_data: dict) -> Destination:
        """Create a new destination for a user using human-centered approach"""
        logger.info(f"=== DestinationService.create_destination called ===")
        logger.info(f"Creating destination for user_id: {user_id} with data: {destination_data}")
        
        try:
            # Validate required fields for new structure
            if not destination_data.get("destination_statement"):
                raise ValueError("Destination statement is required")
            if not destination_data.get("success_vision"):
                raise ValueError("Success vision is required")
            
            # Create Destination instance with enhanced structure
            destination = Destination(
                user_id=user_id,
                destination_statement=destination_data["destination_statement"],
                success_vision=destination_data["success_vision"],
                is_big_idea=destination_data.get("is_big_idea", False),
                big_idea_rank=destination_data.get("big_idea_rank"),
                progress_emoji=destination_data.get("progress_emoji", "😐"),
                progress_notes=destination_data.get("progress_notes"),
                priority=destination_data.get("priority", "medium"),
                category=destination_data.get("category", "personal"),
                ai_suggested=destination_data.get("ai_suggested", False),
                source_documents=destination_data.get("source_documents", []),
                source_entries=destination_data.get("source_entries", []),
                status=destination_data.get("status", "active"),
                tags=destination_data.get("tags", [])
            )
            
            # Add initial progress entry
            initial_progress = ProgressEntry(
                emoji=destination.progress_emoji,
                notes=destination.progress_notes
            )
            destination.progress_history = [initial_progress]
            
            created_destination = await self.destination_repository.create_destination(destination)
            logger.info(f"✅ Successfully created destination with ID: {created_destination.id}")
            
            # Send notification about new destination
            await self._send_destination_notification(created_destination, "created")
            
            return created_destination
            
        except Exception as e:
            logger.error(f"❌ Error creating destination: {e}")
            raise

    async def create_destination_from_suggestion(self, user_id: str, suggestion: DestinationSuggestion) -> Destination:
        """Create a destination from an AI suggestion"""
        logger.info(f"=== DestinationService.create_destination_from_suggestion called ===")
        logger.info(f"Creating destination from suggestion for user_id: {user_id}")
        
        destination_data = {
            "destination_statement": suggestion.destination_statement,
            "success_vision": suggestion.success_vision,
            "ai_suggested": True,
            "source_documents": suggestion.source_documents,
            "source_entries": suggestion.source_entries,
            "progress_emoji": "😐"  # Neutral starting point
        }
        
        return await self.create_destination(user_id, destination_data)

    async def get_destination(self, destination_id: str, user_id: str) -> Optional[Destination]:
        """Retrieve a specific destination, ensuring the user has permission to view it"""
        logger.info(f"=== DestinationService.get_destination called ===")
        logger.info(f"Getting destination_id: {destination_id} for user_id: {user_id}")
        
        try:
            destination = await self.destination_repository.get_destination_by_id(destination_id)
            
            if not destination:
                logger.info(f"Destination {destination_id} not found")
                return None
            
            # Check if user has permission to view this destination
            if destination.user_id != user_id:
                logger.warning(f"User {user_id} attempted to access destination {destination_id} owned by {destination.user_id}")
                raise PermissionError(f"User does not have permission to access this destination")
            
            logger.info(f"✅ Successfully retrieved destination {destination_id}")
            return destination
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting destination: {e}")
            raise

    async def get_destinations(self, user_id: str) -> List[Destination]:
        """Retrieve all destinations for a specific user"""
        logger.info(f"=== DestinationService.get_destinations called ===")
        logger.info(f"Getting all destinations for user_id: {user_id}")
        
        try:
            destinations = await self.destination_repository.get_destinations_by_user_id(user_id)
            logger.info(f"✅ Successfully retrieved {len(destinations)} destinations for user {user_id}")
            return destinations
            
        except Exception as e:
            logger.error(f"❌ Error getting user destinations: {e}")
            raise

    async def get_three_big_ideas(self, user_id: str) -> List[Destination]:
        """Get the three big ideas for a user"""
        logger.info(f"=== DestinationService.get_three_big_ideas called ===")
        logger.info(f"Getting three big ideas for user_id: {user_id}")
        
        try:
            big_ideas = await self.destination_repository.get_three_big_ideas(user_id)
            logger.info(f"✅ Successfully retrieved {len(big_ideas)} big ideas for user {user_id}")
            return big_ideas
            
        except Exception as e:
            logger.error(f"❌ Error getting three big ideas: {e}")
            raise

    async def update_destination(self, destination_id: str, user_id: str, update_data: dict) -> Optional[Destination]:
        """Update a destination, ensuring the user has permission"""
        logger.info(f"=== DestinationService.update_destination called ===")
        logger.info(f"Updating destination_id: {destination_id} for user_id: {user_id} with data: {update_data}")
        
        try:
            # First check if destination exists and user has permission
            existing_destination = await self.get_destination(destination_id, user_id)
            if not existing_destination:
                logger.info(f"Destination {destination_id} not found or user {user_id} has no permission")
                return None
            
            # Validate update data - allow enhanced fields
            allowed_fields = {
                "destination_statement", "success_vision", "is_big_idea", "big_idea_rank",
                "progress_emoji", "progress_notes", "priority", "category",
                "status", "tags", "source_documents", "source_entries",
                # Legacy fields for backward compatibility
                "goal_statement", "title", "description", "target_date",
                "completion_date", "progress_percentage", "notes"
            }
            
            validated_update_data = {}
            for key, value in update_data.items():
                if key in allowed_fields:
                    validated_update_data[key] = value
                else:
                    logger.warning(f"Ignoring invalid update field: {key}")
            
            # Handle legacy field mappings
            if "goal_statement" in validated_update_data:
                validated_update_data["destination_statement"] = validated_update_data.pop("goal_statement")
            
            if not validated_update_data:
                logger.info("No valid fields to update")
                return existing_destination
            
            # Add updated timestamp
            validated_update_data["updated_at"] = datetime.utcnow()
            
            updated_destination = await self.destination_repository.update_destination(destination_id, validated_update_data)
            
            if updated_destination:
                logger.info(f"✅ Successfully updated destination {destination_id}")
                
                # Send notification if status changed to completed
                if validated_update_data.get("status") == "completed":
                    await self._send_destination_notification(updated_destination, "completed")
                elif "progress_emoji" in validated_update_data or "progress_notes" in validated_update_data:
                    await self._send_destination_notification(updated_destination, "progress_updated")
            else:
                logger.warning(f"Destination {destination_id} was not updated")
            
            return updated_destination
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating destination: {e}")
            raise

    async def update_destination_progress(self, destination_id: str, user_id: str, emoji: str, notes: Optional[str] = None, percentage: Optional[int] = None) -> Optional[Destination]:
        """Update destination progress with emoji, notes, and optional percentage"""
        logger.info(f"=== DestinationService.update_destination_progress called ===")
        logger.info(f"Updating progress for destination_id: {destination_id}, user_id: {user_id}, emoji: {emoji}")
        
        try:
            # Get existing destination
            existing_destination = await self.get_destination(destination_id, user_id)
            if not existing_destination:
                logger.info(f"Destination {destination_id} not found or user {user_id} has no permission")
                return None
            
            # Create new progress entry
            progress_entry = ProgressEntry(emoji=emoji, notes=notes, percentage=percentage)
            
            # Update destination with new progress
            update_data = {
                "progress_emoji": emoji,
                "progress_notes": notes,
                "updated_at": datetime.utcnow()
            }
            
            if percentage is not None:
                update_data["progress_percentage"] = percentage
            
            # Add to progress history
            progress_history = existing_destination.progress_history or []
            progress_history.append(progress_entry)
            update_data["progress_history"] = [entry.model_dump() for entry in progress_history]
            
            updated_destination = await self.destination_repository.update_destination(destination_id, update_data)
            
            if updated_destination:
                logger.info(f"✅ Successfully updated progress for destination {destination_id}")
                
                # Send notification about progress update
                await self._send_destination_notification(updated_destination, "progress_updated")
            else:
                logger.warning(f"Progress update failed for destination {destination_id}")
            
            return updated_destination
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error updating destination progress: {e}")
            raise

    async def get_progress_timeline(self, destination_id: str, user_id: str) -> List[ProgressEntry]:
        """Get the progress timeline for a destination"""
        logger.info(f"=== DestinationService.get_progress_timeline called ===")
        logger.info(f"Getting progress timeline for destination_id: {destination_id}, user_id: {user_id}")
        
        try:
            destination = await self.get_destination(destination_id, user_id)
            if not destination:
                logger.info(f"Destination {destination_id} not found or user {user_id} has no permission")
                return []
            
            progress_timeline = destination.progress_history or []
            logger.info(f"✅ Retrieved {len(progress_timeline)} progress entries for destination {destination_id}")
            return progress_timeline
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error getting progress timeline: {e}")
            raise

    async def suggest_destinations_from_documents(self, user_id: str, document_ids: List[str]) -> List[DestinationSuggestion]:
        """Generate AI-powered destination suggestions based on uploaded documents"""
        logger.info(f"=== DestinationService.suggest_destinations_from_documents called ===")
        logger.info(f"Generating destination suggestions for user_id: {user_id} from {len(document_ids)} documents")
        
        try:
            # TODO: Implement AI analysis of documents to generate destination suggestions
            # This is a placeholder implementation
            
            # For now, return some example suggestions
            suggestions = [
                DestinationSuggestion(
                    destination_statement="Improve communication with my team",
                    success_vision="My team feels heard, we have fewer misunderstandings, and people seem more engaged when I speak",
                    source_documents=document_ids
                ),
                DestinationSuggestion(
                    destination_statement="Develop better work-life balance",
                    success_vision="I feel more energized at work and more present at home, with clear boundaries between the two",
                    source_documents=document_ids
                ),
                DestinationSuggestion(
                    destination_statement="Build confidence in decision-making",
                    success_vision="I trust my instincts more, make decisions without excessive second-guessing, and feel proud of my choices",
                    source_documents=document_ids
                )
            ]
            
            logger.info(f"✅ Generated {len(suggestions)} destination suggestions for user {user_id}")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error generating destination suggestions: {e}")
            raise

    async def enhance_success_vision(self, destination_statement: str, user_context: dict) -> List[str]:
        """Provide success vision suggestions based on destination statement and user context"""
        logger.info(f"=== DestinationService.enhance_success_vision called ===")
        logger.info(f"Enhancing success vision for destination: {destination_statement}")
        
        try:
            # TODO: Implement AI-powered success vision enhancement
            # This is a placeholder implementation
            
            suggestions = [
                "I feel more confident and comfortable in situations related to this destination",
                "Others notice positive changes in how I approach this area",
                "I experience less stress and more satisfaction when dealing with this topic",
                "I can see clear progress in small, daily interactions and decisions"
            ]
            
            logger.info(f"✅ Generated {len(suggestions)} success vision suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Error enhancing success vision: {e}")
            raise

    async def delete_destination(self, destination_id: str, user_id: str) -> bool:
        """Delete a destination, ensuring the user has permission"""
        logger.info(f"=== DestinationService.delete_destination called ===")
        logger.info(f"Deleting destination_id: {destination_id} for user_id: {user_id}")
        
        try:
            # First check if destination exists and user has permission
            existing_destination = await self.get_destination(destination_id, user_id)
            if not existing_destination:
                logger.info(f"Destination {destination_id} not found or user {user_id} has no permission")
                return False
            
            success = await self.destination_repository.delete_destination(destination_id)
            
            if success:
                logger.info(f"✅ Successfully deleted destination {destination_id}")
            else:
                logger.warning(f"Destination {destination_id} was not deleted")
            
            return success
            
        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"❌ Error deleting destination: {e}")
            raise

    async def get_destinations_by_status(self, user_id: str, status: str) -> List[Destination]:
        """Get all destinations for a user filtered by status"""
        logger.info(f"=== DestinationService.get_destinations_by_status called ===")
        logger.info(f"Getting destinations for user_id: {user_id} with status: {status}")
        
        try:
            all_destinations = await self.get_destinations(user_id)
            filtered_destinations = [dest for dest in all_destinations if dest.status == status]
            
            logger.info(f"✅ Found {len(filtered_destinations)} destinations with status '{status}' for user {user_id}")
            return filtered_destinations
            
        except Exception as e:
            logger.error(f"❌ Error getting destinations by status: {e}")
            raise

    async def get_destinations_by_priority(self, user_id: str, priority: str) -> List[Destination]:
        """Get all destinations for a user filtered by priority"""
        logger.info(f"=== DestinationService.get_destinations_by_priority called ===")
        logger.info(f"Getting destinations for user_id: {user_id} with priority: {priority}")
        
        try:
            all_destinations = await self.get_destinations(user_id)
            filtered_destinations = [dest for dest in all_destinations if dest.priority == priority]
            
            logger.info(f"✅ Found {len(filtered_destinations)} destinations with priority '{priority}' for user {user_id}")
            return filtered_destinations
            
        except Exception as e:
            logger.error(f"❌ Error getting destinations by priority: {e}")
            raise

    # Backward compatibility methods
    async def create_goal(self, user_id: str, goal_data: dict) -> Destination:
        """Backward compatibility wrapper for create_destination"""
        logger.info("Using backward compatibility wrapper: create_goal -> create_destination")
        
        # Convert goal_statement to destination_statement if present
        if "goal_statement" in goal_data:
            goal_data["destination_statement"] = goal_data.pop("goal_statement")
        
        return await self.create_destination(user_id, goal_data)

    async def get_goal(self, goal_id: str, user_id: str) -> Optional[Destination]:
        """Backward compatibility wrapper for get_destination"""
        logger.info("Using backward compatibility wrapper: get_goal -> get_destination")
        return await self.get_destination(goal_id, user_id)

    async def get_all_user_goals(self, user_id: str) -> List[Destination]:
        """Backward compatibility wrapper for get_destinations"""
        logger.info("Using backward compatibility wrapper: get_all_user_goals -> get_destinations")
        return await self.get_destinations(user_id)

    async def update_goal(self, goal_id: str, user_id: str, update_data: dict) -> Optional[Destination]:
        """Backward compatibility wrapper for update_destination"""
        logger.info("Using backward compatibility wrapper: update_goal -> update_destination")
        return await self.update_destination(goal_id, user_id, update_data)

    async def update_progress_emotion(self, goal_id: str, user_id: str, emoji: str, notes: Optional[str] = None) -> Optional[Destination]:
        """Backward compatibility wrapper for update_destination_progress"""
        logger.info("Using backward compatibility wrapper: update_progress_emotion -> update_destination_progress")
        return await self.update_destination_progress(goal_id, user_id, emoji, notes)

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Backward compatibility wrapper for delete_destination"""
        logger.info("Using backward compatibility wrapper: delete_goal -> delete_destination")
        return await self.delete_destination(goal_id, user_id)

    async def suggest_goals_from_documents(self, user_id: str, document_ids: List[str]) -> List[GoalSuggestion]:
        """Backward compatibility wrapper for suggest_destinations_from_documents"""
        logger.info("Using backward compatibility wrapper: suggest_goals_from_documents -> suggest_destinations_from_documents")
        
        destination_suggestions = await self.suggest_destinations_from_documents(user_id, document_ids)
        
        # Convert DestinationSuggestion to GoalSuggestion
        goal_suggestions = []
        for dest_suggestion in destination_suggestions:
            goal_suggestion = GoalSuggestion(
                goal_statement=dest_suggestion.destination_statement,
                success_vision=dest_suggestion.success_vision,
                source_documents=dest_suggestion.source_documents
            )
            goal_suggestions.append(goal_suggestion)
        
        return goal_suggestions

    async def create_goal_from_suggestion(self, user_id: str, suggestion: GoalSuggestion):
        """Create goal from suggestion (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: create_goal_from_suggestion")
        
        try:
            # Convert GoalSuggestion to DestinationSuggestion
            dest_suggestion = DestinationSuggestion(
                destination_statement=suggestion.goal_statement,
                success_vision=suggestion.success_vision,
                source_documents=suggestion.source_documents
            )
            
            destination = await self.create_destination_from_suggestion(user_id, dest_suggestion)
            return self._destination_to_goal(destination)
        except Exception as e:
            logger.error(f"Error creating goal from suggestion: {e}")
            raise

    async def get_goal_wrapper(self, goal_id: str, user_id: str):
        """Get goal by ID (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: get_goal -> get_destination")
        
        try:
            destination = await self.get_destination(goal_id, user_id)
            if destination:
                return self._destination_to_goal(destination)
            return None
        except Exception as e:
            logger.error(f"Error getting goal: {e}")
            raise

    async def get_all_user_goals_wrapper(self, user_id: str):
        """Get all goals for user (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: get_all_user_goals -> get_destinations")
        
        try:
            destinations = await self.get_destinations(user_id)
            return [self._destination_to_goal(dest) for dest in destinations]
        except Exception as e:
            logger.error(f"Error getting user goals: {e}")
            raise

    async def update_goal_wrapper(self, goal_id: str, user_id: str, update_data: dict):
        """Update goal (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: update_goal -> update_destination")
        
        try:
            # Convert goal_statement to destination_statement if present
            destination_update_data = update_data.copy()
            if "goal_statement" in destination_update_data:
                destination_update_data["destination_statement"] = destination_update_data.pop("goal_statement")
            
            destination = await self.update_destination(goal_id, user_id, destination_update_data)
            if destination:
                return self._destination_to_goal(destination)
            return None
        except Exception as e:
            logger.error(f"Error updating goal: {e}")
            raise

    async def update_progress_emotion_wrapper(self, goal_id: str, user_id: str, emoji: str, notes: Optional[str] = None):
        """Update progress emotion (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: update_progress_emotion -> update_destination_progress")
        
        try:
            destination = await self.update_destination_progress(goal_id, user_id, emoji, notes)
            if destination:
                return self._destination_to_goal(destination)
            return None
        except Exception as e:
            logger.error(f"Error updating progress emotion: {e}")
            raise

    async def delete_goal_wrapper(self, goal_id: str, user_id: str) -> bool:
        """Delete goal (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: delete_goal -> delete_destination")
        
        try:
            return await self.delete_destination(goal_id, user_id)
        except Exception as e:
            logger.error(f"Error deleting goal: {e}")
            raise

    async def get_progress_timeline_wrapper(self, goal_id: str, user_id: str):
        """Get progress timeline (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: get_progress_timeline")
        
        try:
            return await self.get_progress_timeline(goal_id, user_id)
        except Exception as e:
            logger.error(f"Error getting progress timeline: {e}")
            raise

    async def get_goals_by_status_wrapper(self, user_id: str, status: str):
        """Get goals by status (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: get_goals_by_status -> get_destinations_by_status")
        
        try:
            destinations = await self.get_destinations_by_status(user_id, status)
            return [self._destination_to_goal(dest) for dest in destinations]
        except Exception as e:
            logger.error(f"Error getting goals by status: {e}")
            raise

    async def get_goals_by_priority_wrapper(self, user_id: str, priority: str):
        """Get goals by priority (backward compatibility wrapper)"""
        logger.info("Using backward compatibility wrapper: get_goals_by_priority -> get_destinations_by_priority")
        
        try:
            destinations = await self.get_destinations_by_priority(user_id, priority)
            return [self._destination_to_goal(dest) for dest in destinations]
        except Exception as e:
            logger.error(f"Error getting goals by priority: {e}")
            raise
    
    def _destination_to_goal(self, destination):
        """Convert Destination model to Goal model for backward compatibility"""
        try:
            from app.models.goal import Goal
            
            # Map destination fields to goal fields
            goal_data = {
                "user_id": destination.user_id,
                "goal_statement": destination.destination_statement,
                "success_vision": destination.success_vision,
                "progress_emoji": destination.progress_emoji,
                "progress_notes": destination.progress_notes,
                "progress_history": destination.progress_history or [],
                "ai_suggested": destination.ai_suggested,
                "source_documents": destination.source_documents,
                "status": destination.status,
                "tags": destination.tags,
                "created_at": destination.created_at,
                "updated_at": destination.updated_at
            }
            
            # Create Goal instance
            goal = Goal(**goal_data)
            goal.id = destination.id
            
            return goal
            
        except Exception as e:
            logger.error(f"Error converting destination to goal: {e}")
            raise

    async def _send_destination_notification(self, destination: Destination, update_type: str):
        """Send notification about destination updates"""
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            await notification_service.notify_destination_update(
                user_id=destination.user_id,
                destination_id=str(destination.id),
                destination_title=destination.destination_statement,
                update_type=update_type
            )
            
            logger.info(f"✅ Sent {update_type} notification for destination: {destination.id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending destination notification: {e}")
            # Don't raise the error as the destination operation was successful