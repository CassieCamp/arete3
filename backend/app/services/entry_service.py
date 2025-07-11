from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.entry import Entry, EntryStatus, EntryType
from app.repositories.entry_repository import EntryRepository
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.services.ai_service import AIService
from app.services.text_extraction_service import TextExtractionService
from app.core.config import settings
import logging
import json
import time

logger = logging.getLogger(__name__)


class EntryService:
    def __init__(self):
        self.entry_repository = EntryRepository()
        self.relationship_repository = CoachingRelationshipRepository()
        self.ai_service = AIService()
        self.text_extraction_service = TextExtractionService()

    async def create_entry(
        self,
        user_id: str,
        entry_type: EntryType,
        content: str,
        title: Optional[str] = None,
        coaching_relationship_id: Optional[str] = None,
        session_date: Optional[str] = None,
        source_document_id: Optional[str] = None
    ) -> Entry:
        """
        Create a new entry (session or fresh thought).
        
        Handles both paired (with coaching relationship) and unpaired entries.
        Processes content through AI analysis and generates insights.
        """
        try:
            logger.info(f"=== EntryService.create_entry called ===")
            logger.info(f"user_id: {user_id}, entry_type: {entry_type}")
            
            # Determine coach and client user IDs
            coach_user_id = None
            client_user_id = user_id
            
            if coaching_relationship_id:
                # Validate coaching relationship exists and user has access
                relationship = await self.relationship_repository.get_relationship_by_id(
                    coaching_relationship_id
                )
                if not relationship:
                    raise ValueError("Coaching relationship not found")
                
                # Validate user is part of the relationship
                if user_id not in [relationship.coach_user_id, relationship.client_user_id]:
                    raise ValueError("User not authorized for this coaching relationship")
                
                coach_user_id = relationship.coach_user_id
                client_user_id = relationship.client_user_id
            
            # Create pending entry record
            pending_entry = Entry(
                entry_type=entry_type,
                title=title or "Processing...",
                coaching_relationship_id=coaching_relationship_id,
                client_user_id=client_user_id,
                coach_user_id=coach_user_id,
                session_date=datetime.fromisoformat(session_date.replace('Z', '+00:00')) if session_date else None,
                transcript_content=content if entry_type == EntryType.SESSION else None,
                content=content if entry_type == EntryType.FRESH_THOUGHT else None,
                status=EntryStatus.PROCESSING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save pending entry
            saved_entry = await self.entry_repository.create_entry(pending_entry)
            logger.info(f"Created pending entry: {saved_entry.id}")
            
            # Generate AI analysis
            analysis_result = await self._generate_entry_insights(content, entry_type)
            
            # Generate AI title if not provided
            if not title:
                title = await self._generate_entry_title(content, entry_type)
            
            # Update entry with analysis results
            completed_entry = self._build_entry_from_analysis(
                saved_entry, 
                analysis_result, 
                title,
                content
            )
            
            # Save completed entry
            updated_entry = await self.entry_repository.update_entry(
                str(saved_entry.id),
                completed_entry.model_dump(exclude={"id"})
            )
            
            logger.info(f"✅ Successfully generated entry: {updated_entry.id}")
            
            # Send notification
            await self._send_entry_notifications(updated_entry)
            
            return updated_entry
            
        except Exception as e:
            logger.error(f"❌ Error creating entry: {e}")
            # Update entry status to failed if it was created
            if 'saved_entry' in locals():
                await self.entry_repository.update_entry(
                    str(saved_entry.id),
                    {"status": EntryStatus.FAILED, "processing_error": str(e)}
                )
            raise

    async def get_entries(
        self,
        user_id: str,
        entry_type: Optional[EntryType] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Entry]:
        """
        Get entries for a user with optional filtering and freemium gating.
        """
        try:
            logger.info(f"=== EntryService.get_entries called ===")
            logger.info(f"user_id: {user_id}, entry_type: {entry_type}")
            
            # Apply freemium gating
            can_access = await self._check_freemium_access(user_id, limit, offset)
            if not can_access:
                # Return limited entries for freemium users
                limit = min(limit, 3)
                offset = 0
            
            entries = await self.entry_repository.get_entries_by_user(
                user_id=user_id,
                entry_type=entry_type.value if entry_type else None,
                limit=limit,
                offset=offset
            )
            
            logger.info(f"✅ Retrieved {len(entries)} entries for user")
            return entries
            
        except Exception as e:
            logger.error(f"❌ Error fetching entries: {e}")
            raise

    async def get_entry_insights(self, entry_id: str, user_id: str) -> Optional[Entry]:
        """
        Get entry insights with freemium gating.
        """
        try:
            logger.info(f"=== EntryService.get_entry_insights called ===")
            logger.info(f"entry_id: {entry_id}, user_id: {user_id}")
            
            entry = await self.entry_repository.get_entry_by_id(entry_id)
            if not entry:
                return None
            
            # Validate user has access to this entry
            if entry.client_user_id != user_id and entry.coach_user_id != user_id:
                raise ValueError("User not authorized to view this entry")
            
            # Apply freemium gating for insights
            can_access_insights = await self._check_freemium_insights_access(user_id)
            if not can_access_insights:
                # Return entry without detailed insights for freemium users
                entry.celebrations = []
                entry.intentions = []
                entry.client_discoveries = []
                entry.goal_progress = []
                entry.powerful_questions = []
                entry.action_items = []
                entry.emotional_shifts = []
                entry.values_beliefs = []
                entry.communication_patterns = None
            
            return entry
            
        except Exception as e:
            logger.error(f"❌ Error fetching entry insights: {e}")
            raise

    async def accept_detected_goals(self, entry_id: str, user_id: str, accepted_goal_indices: List[int]) -> bool:
        """
        Accept detected goals and convert them to destinations.
        """
        try:
            logger.info(f"=== EntryService.accept_detected_goals called ===")
            logger.info(f"entry_id: {entry_id}, user_id: {user_id}")
            
            # Get the entry
            entry = await self.entry_repository.get_entry_by_id(entry_id)
            if not entry:
                raise ValueError("Entry not found")
            
            # Validate user has access
            if entry.client_user_id != user_id:
                raise ValueError("User not authorized to accept goals for this entry")
            
            # Mark goals as accepted in the entry
            success = await self.entry_repository.accept_detected_goals(entry_id, accepted_goal_indices)
            
            if success:
                # Create destinations from accepted goals
                from app.services.destination_service import DestinationService
                destination_service = DestinationService()
                
                for i in accepted_goal_indices:
                    if i < len(entry.detected_goals):
                        detected_goal = entry.detected_goals[i]
                        destination_data = {
                            "destination_statement": detected_goal.goal_statement,
                            "success_vision": "AI-generated goal from entry analysis",
                            "ai_suggested": True,
                            "source_entries": [str(entry.id)],
                            "priority": "medium",
                            "category": "personal"
                        }
                        
                        await destination_service.create_destination(user_id, destination_data)
                
                logger.info(f"✅ Successfully accepted {len(accepted_goal_indices)} goals")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error accepting detected goals: {e}")
            raise

    async def _generate_entry_insights(self, content: str, entry_type: EntryType) -> Dict[str, Any]:
        """
        Generate AI insights from entry content.
        """
        start_time = time.time()
        
        try:
            logger.info(f"=== Generating entry insights ===")
            logger.info(f"content length: {len(content)} characters, type: {entry_type}")
            
            # Build analysis prompt based on entry type
            if entry_type == EntryType.SESSION:
                prompt = self._build_session_analysis_prompt(content)
            else:
                prompt = self._build_fresh_thought_analysis_prompt(content)
            
            # Call AI provider
            if settings.ai_provider == "anthropic" and self.ai_service.anthropic_client:
                result = await self._call_anthropic_for_analysis(prompt)
            elif settings.ai_provider == "openai" and self.ai_service.openai_client:
                result = await self._call_openai_for_analysis(prompt)
            else:
                raise Exception("No AI provider available for entry analysis")
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Entry analysis completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in entry analysis: {e}")
            raise

    async def _generate_entry_title(self, content: str, entry_type: EntryType) -> str:
        """
        Generate AI title for entry.
        """
        try:
            prompt = f"""
            Generate a concise, descriptive title (max 60 characters) for this {entry_type.value}:
            
            Content: {content[:500]}...
            
            Return only the title, no quotes or additional text.
            """
            
            if settings.ai_provider == "anthropic" and self.ai_service.anthropic_client:
                response = await self.ai_service.anthropic_client.messages.create(
                    model=settings.ai_model,
                    max_tokens=50,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
            elif settings.ai_provider == "openai" and self.ai_service.openai_client:
                response = await self.ai_service.openai_client.chat.completions.create(
                    model=settings.ai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=50,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                return f"{entry_type.value.title()} Entry"
                
        except Exception as e:
            logger.error(f"Error generating title: {e}")
            return f"{entry_type.value.title()} Entry"

    def _build_session_analysis_prompt(self, content: str) -> str:
        """Build analysis prompt for session entries"""
        return f"""
        Analyze this coaching session transcript and extract insights aligned with ICF coaching competencies.
        
        TRANSCRIPT:
        {content}
        
        Extract the following insights in JSON format:
        {{
          "celebrations": [{{ "description": "...", "significance": "...", "evidence": ["..."] }}],
          "intentions": [{{ "behavior_change": "...", "commitment_level": "...", "timeline": "...", "support_needed": ["..."] }}],
          "client_discoveries": [{{ "insight": "...", "depth_level": "...", "emotional_response": "...", "evidence": ["..."] }}],
          "goal_progress": [{{ "goal_area": "...", "progress_description": "...", "progress_level": "...", "barriers_identified": ["..."], "next_steps": ["..."] }}],
          "powerful_questions": [{{ "question": "...", "impact_description": "...", "client_response_summary": "...", "breakthrough_level": "..." }}],
          "action_items": [{{ "action": "...", "timeline": "...", "accountability_measure": "...", "client_commitment_level": "..." }}],
          "emotional_shifts": [{{ "initial_state": "...", "final_state": "...", "shift_description": "...", "catalyst": "..." }}],
          "values_beliefs": [{{ "type": "...", "description": "...", "impact_on_goals": "...", "exploration_depth": "..." }}],
          "detected_goals": [{{ "goal_statement": "...", "confidence": 0.8 }}]
        }}
        
        Return only valid JSON.
        """

    def _build_fresh_thought_analysis_prompt(self, content: str) -> str:
        """Build analysis prompt for fresh thought entries"""
        return f"""
        Analyze this personal reflection/thought and extract meaningful insights.
        
        CONTENT:
        {content}
        
        Extract insights in JSON format:
        {{
          "celebrations": [{{ "description": "...", "significance": "...", "evidence": ["..."] }}],
          "intentions": [{{ "behavior_change": "...", "commitment_level": "...", "timeline": "...", "support_needed": ["..."] }}],
          "client_discoveries": [{{ "insight": "...", "depth_level": "...", "emotional_response": "...", "evidence": ["..."] }}],
          "emotional_shifts": [{{ "initial_state": "...", "final_state": "...", "shift_description": "...", "catalyst": "..." }}],
          "values_beliefs": [{{ "type": "...", "description": "...", "impact_on_goals": "...", "exploration_depth": "..." }}],
          "detected_goals": [{{ "goal_statement": "...", "confidence": 0.7 }}]
        }}
        
        Return only valid JSON.
        """

    async def _call_anthropic_for_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API for analysis"""
        try:
            response = await self.ai_service.anthropic_client.messages.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Anthropic API error in entry analysis: {e}")
            raise

    async def _call_openai_for_analysis(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API for analysis"""
        try:
            response = await self.ai_service.openai_client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an expert coaching analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                timeout=settings.ai_timeout_seconds
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI API error in entry analysis: {e}")
            raise

    def _build_entry_from_analysis(self, base_entry: Entry, analysis: dict, title: str, content: str) -> Entry:
        """Build complete entry object from AI analysis results"""
        
        # Map analysis results to entry model
        from app.models.entry import (
            Celebration, Intention, ClientDiscovery, GoalProgress, 
            PowerfulQuestion, ActionItem, EmotionalShift, ValuesBeliefs, DetectedGoal
        )
        
        base_entry.title = title
        base_entry.celebrations = [Celebration(**c) for c in analysis.get("celebrations", [])]
        base_entry.intentions = [Intention(**i) for i in analysis.get("intentions", [])]
        base_entry.client_discoveries = [ClientDiscovery(**d) for d in analysis.get("client_discoveries", [])]
        base_entry.goal_progress = [GoalProgress(**g) for g in analysis.get("goal_progress", [])]
        base_entry.powerful_questions = [PowerfulQuestion(**q) for q in analysis.get("powerful_questions", [])]
        base_entry.action_items = [ActionItem(**a) for a in analysis.get("action_items", [])]
        base_entry.emotional_shifts = [EmotionalShift(**e) for e in analysis.get("emotional_shifts", [])]
        base_entry.values_beliefs = [ValuesBeliefs(**v) for v in analysis.get("values_beliefs", [])]
        base_entry.detected_goals = [DetectedGoal(**g) for g in analysis.get("detected_goals", [])]
        
        # Set completion status
        base_entry.status = EntryStatus.COMPLETED
        base_entry.completed_at = datetime.utcnow()
        
        return base_entry

    async def _check_freemium_access(self, user_id: str, limit: int, offset: int) -> bool:
        """Check if user can access entries based on freemium status"""
        try:
            from app.services.freemium_service import FreemiumService
            freemium_service = FreemiumService()
            
            freemium_status = await freemium_service.get_freemium_status(user_id)
            
            # If user has a coach, they have full access
            if freemium_status.get("has_coach", False):
                return True
            
            # For freemium users, limit access
            entries_count = freemium_status.get("entries_count", 0)
            max_free_entries = freemium_status.get("max_free_entries", 3)
            
            return entries_count <= max_free_entries
            
        except Exception as e:
            logger.error(f"Error checking freemium access: {e}")
            return True  # Default to allowing access

    async def _check_freemium_insights_access(self, user_id: str) -> bool:
        """Check if user can access detailed insights"""
        try:
            from app.services.freemium_service import FreemiumService
            freemium_service = FreemiumService()
            
            freemium_status = await freemium_service.get_freemium_status(user_id)
            
            # If user has a coach, they have full access to insights
            return freemium_status.get("has_coach", False)
            
        except Exception as e:
            logger.error(f"Error checking freemium insights access: {e}")
            return True  # Default to allowing access

    async def _send_entry_notifications(self, entry: Entry):
        """Send notifications when entry is completed"""
        try:
            from app.services.notification_service import NotificationService
            notification_service = NotificationService()
            
            # Notify the client
            await notification_service.notify_entry_completed(
                user_id=entry.client_user_id,
                entry_id=str(entry.id),
                entry_title=entry.title
            )
            
            # Notify the coach if this is a paired entry
            if entry.coach_user_id:
                await notification_service.notify_entry_completed(
                    user_id=entry.coach_user_id,
                    entry_id=str(entry.id),
                    entry_title=entry.title
                )
                
            logger.info(f"✅ Sent notifications for entry: {entry.id}")
            
        except Exception as e:
            logger.error(f"❌ Error sending entry notifications: {e}")
            # Don't raise the error as the entry was created successfully