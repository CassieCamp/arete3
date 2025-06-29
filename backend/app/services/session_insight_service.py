from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.session_insight import (
    SessionInsight, SessionInsightStatus, Celebration, Intention, 
    ClientDiscovery, GoalProgress, CoachingPresence, PowerfulQuestion,
    ActionItem, EmotionalShift, ValuesBeliefs, CommunicationPattern,
    SessionMetadata
)
from app.repositories.session_insight_repository import SessionInsightRepository
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.services.ai_service import AIService
from app.services.text_extraction_service import TextExtractionService
from app.core.config import settings
import logging
import json
import time

logger = logging.getLogger(__name__)


class SessionInsightService:
    def __init__(self):
        self.insight_repository = SessionInsightRepository()
        self.relationship_repository = CoachingRelationshipRepository()
        self.ai_service = AIService()
        self.text_extraction_service = TextExtractionService()

    async def create_insight_from_transcript(
        self,
        coaching_relationship_id: str,
        transcript_content: str,
        created_by: str,
        session_date: Optional[str] = None,
        session_title: Optional[str] = None,
        source_document_id: Optional[str] = None
    ) -> SessionInsight:
        """
        Create session insight from transcript content.
        
        Validates relationship access, processes transcript through AI analysis,
        and creates structured insight record.
        """
        try:
            logger.info(f"=== SessionInsightService.create_insight_from_transcript called ===")
            logger.info(f"relationship_id: {coaching_relationship_id}, created_by: {created_by}")
            
            # Validate coaching relationship exists and user has access
            relationship = await self.relationship_repository.get_relationship_by_id(
                coaching_relationship_id
            )
            if not relationship:
                raise ValueError("Coaching relationship not found")
            
            # Validate user is part of the relationship
            if created_by not in [relationship.coach_user_id, relationship.client_user_id]:
                raise ValueError("User not authorized for this coaching relationship")
            
            # Create pending insight record
            pending_insight = SessionInsight(
                coaching_relationship_id=coaching_relationship_id,
                client_user_id=relationship.client_user_id,
                coach_user_id=relationship.coach_user_id,
                session_date=datetime.fromisoformat(session_date.replace('Z', '+00:00')) if session_date else None,
                session_title=session_title,
                transcript_source="file_upload" if source_document_id else "text_input",
                source_document_id=source_document_id,
                session_summary="Processing transcript...",
                overall_session_quality="Average",  # Default value, will be updated after AI analysis
                status=SessionInsightStatus.PROCESSING,
                created_by=created_by
            )
            
            # Save pending insight
            saved_insight = await self.insight_repository.create_insight(pending_insight)
            logger.info(f"Created pending session insight: {saved_insight.id}")
            
            # Generate AI analysis
            session_context = {
                "relationship_duration": "Unknown",  # Could be calculated from relationship
                "previous_session_count": await self._get_previous_session_count(coaching_relationship_id)
            }
            
            analysis_result = await self._generate_session_insights(
                transcript_content, 
                session_context
            )
            
            # Update insight with analysis results
            completed_insight = self._build_insight_from_analysis(
                saved_insight, 
                analysis_result, 
                transcript_content
            )
            
            # Save completed insight
            updated_insight = await self.insight_repository.update_insight(
                str(saved_insight.id),
                completed_insight.model_dump(exclude={"id"})
            )
            
            logger.info(f"✅ Successfully generated session insight: {updated_insight.id}")
            return updated_insight
            
        except Exception as e:
            logger.error(f"❌ Error creating session insight: {e}")
            # Update insight status to failed if it was created
            if 'saved_insight' in locals():
                await self.insight_repository.update_insight(
                    str(saved_insight.id),
                    {"status": SessionInsightStatus.FAILED, "processing_error": str(e)}
                )
            raise

    async def get_insights_for_relationship(
        self,
        relationship_id: str,
        requesting_user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[SessionInsight]:
        """
        Get session insights for a coaching relationship.
        
        Validates user access and returns paginated insights.
        """
        try:
            # Validate relationship access
            relationship = await self.relationship_repository.get_relationship_by_id(relationship_id)
            if not relationship:
                raise ValueError("Coaching relationship not found")
            
            if requesting_user_id not in [relationship.coach_user_id, relationship.client_user_id]:
                raise ValueError("User not authorized for this coaching relationship")
            
            # Fetch insights
            insights = await self.insight_repository.get_insights_by_relationship(
                relationship_id, limit, offset
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error fetching insights for relationship {relationship_id}: {e}")
            raise

    async def get_insight_by_id(
        self,
        insight_id: str,
        requesting_user_id: str
    ) -> Optional[SessionInsight]:
        """Get session insight by ID with access validation"""
        try:
            insight = await self.insight_repository.get_insight_by_id(insight_id)
            if not insight:
                return None
            
            # Validate user has access to this insight
            if requesting_user_id not in [insight.coach_user_id, insight.client_user_id]:
                raise ValueError("User not authorized to view this insight")
            
            return insight
            
        except Exception as e:
            logger.error(f"Error fetching insight {insight_id}: {e}")
            raise

    async def delete_insight(
        self,
        insight_id: str,
        requesting_user_id: str
    ) -> bool:
        """Delete session insight with permission validation"""
        try:
            insight = await self.insight_repository.get_insight_by_id(insight_id)
            if not insight:
                return False
            
            # Only creator or coach can delete insights
            if requesting_user_id not in [insight.created_by, insight.coach_user_id]:
                raise ValueError("User not authorized to delete this insight")
            
            return await self.insight_repository.delete_insight(insight_id)
            
        except Exception as e:
            logger.error(f"Error deleting insight {insight_id}: {e}")
            raise

    async def _get_previous_session_count(self, relationship_id: str) -> int:
        """Get count of previous sessions for context"""
        try:
            insights = await self.insight_repository.get_insights_by_relationship(
                relationship_id, limit=1000, offset=0
            )
            return len(insights)
        except Exception as e:
            logger.error(f"Error counting previous sessions: {e}")
            return 0

    async def _generate_session_insights(
        self,
        transcript_content: str,
        session_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive session insights from transcript.
        
        Uses ICF-aligned analysis framework to extract coaching-relevant insights.
        """
        start_time = time.time()
        
        try:
            logger.info(f"=== Generating session insights ===")
            logger.info(f"transcript length: {len(transcript_content)} characters")
            
            # Build analysis prompt
            prompt = self._build_session_analysis_prompt(transcript_content, session_context)
            
            # Call AI provider
            if settings.ai_provider == "anthropic" and self.ai_service.anthropic_client:
                result = await self._call_anthropic_for_session(prompt)
            elif settings.ai_provider == "openai" and self.ai_service.openai_client:
                result = await self._call_openai_for_session(prompt)
            else:
                raise Exception("No AI provider available for session analysis")
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Session analysis completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in session analysis: {e}")
            raise

    def _build_session_analysis_prompt(self, transcript: str, context: Dict) -> str:
        """Build comprehensive session analysis prompt based on ICF competencies"""
        
        return f"""
Analyze this coaching session transcript and extract insights aligned with ICF coaching competencies.

TRANSCRIPT:
{transcript}

CONTEXT:
- Client-Coach Relationship: {context.get('relationship_duration', 'Unknown')}
- Previous Sessions: {context.get('previous_session_count', 0)}

Extract the following insights in JSON format:

{{
  "celebration": {{
    "description": "A specific win or achievement to celebrate",
    "significance": "Why this is meaningful for the client",
    "evidence": ["Supporting quotes from transcript"]
  }},
  "intention": {{
    "behavior_change": "Specific behavior change discussed",
    "commitment_level": "Strong/Moderate/Exploratory",
    "timeline": "When client intends to implement",
    "support_needed": ["Types of support client identified"]
  }},
  "client_discoveries": [
    {{
      "insight": "New self-awareness the client gained",
      "depth_level": "Surface/Moderate/Deep",
      "emotional_response": "Client's reaction to discovery",
      "evidence": ["Supporting quotes"]
    }}
  ],
  "goal_progress": [
    {{
      "goal_area": "Specific goal or area discussed",
      "progress_description": "Nature of progress made",
      "progress_level": "Significant/Moderate/Minimal/Setback",
      "barriers_identified": ["Obstacles mentioned"],
      "next_steps": ["Specific actions identified"]
    }}
  ],
  "coaching_presence": {{
    "client_engagement_level": "High/Moderate/Low",
    "rapport_quality": "Description of relationship quality",
    "trust_indicators": ["Evidence of trust in relationship"],
    "partnership_dynamics": "How coach and client worked together"
  }},
  "powerful_questions": [
    {{
      "question": "Exact question that had impact",
      "impact_description": "How it affected the client",
      "client_response_summary": "Client's response",
      "breakthrough_level": "Major/Moderate/Minor"
    }}
  ],
  "action_items": [
    {{
      "action": "Specific action client committed to",
      "timeline": "When they'll do it",
      "accountability_measure": "How progress will be tracked",
      "client_commitment_level": "High/Medium/Low"
    }}
  ],
  "emotional_shifts": [
    {{
      "initial_state": "Client's emotional state at start",
      "final_state": "Client's emotional state at end",
      "shift_description": "Nature of the change",
      "catalyst": "What caused the shift"
    }}
  ],
  "values_beliefs": [
    {{
      "type": "Core Value/Limiting Belief/Empowering Belief",
      "description": "The value or belief identified",
      "impact_on_goals": "How it affects client's goals",
      "exploration_depth": "How deeply it was explored"
    }}
  ],
  "communication_patterns": {{
    "processing_style": "Visual/Auditory/Kinesthetic/Mixed",
    "expression_patterns": ["How client typically expresses themselves"],
    "communication_preferences": ["Preferred communication styles"],
    "notable_changes": ["Any changes from previous patterns"]
  }},
  "session_summary": "2-3 sentence overview of the session",
  "key_themes": ["3-5 main themes from the session"],
  "overall_session_quality": "Excellent/Good/Average/Needs Improvement"
}}

ANALYSIS GUIDELINES:
- Only extract information explicitly present in the transcript
- Focus on coaching-relevant insights that support client development
- Maintain confidentiality and professional tone
- If insufficient evidence exists for any section, omit rather than speculate
- Prioritize insights that will be valuable for future sessions

Return only valid JSON matching the exact structure above.
"""

    async def _call_anthropic_for_session(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API for session analysis"""
        try:
            response = await self.ai_service.anthropic_client.messages.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Anthropic API error in session analysis: {e}")
            raise

    async def _call_openai_for_session(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API for session analysis"""
        try:
            response = await self.ai_service.openai_client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an expert coaching analyst specializing in ICF-aligned session analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                timeout=settings.ai_timeout_seconds
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI API error in session analysis: {e}")
            raise

    def _build_insight_from_analysis(
        self, 
        base_insight: SessionInsight, 
        analysis: dict, 
        transcript_content: str
    ) -> SessionInsight:
        """Build complete insight object from AI analysis results"""
        
        # Map analysis results to insight model
        base_insight.celebration = Celebration(**analysis["celebration"]) if analysis.get("celebration") else None
        base_insight.intention = Intention(**analysis["intention"]) if analysis.get("intention") else None
        base_insight.client_discoveries = [ClientDiscovery(**d) for d in analysis.get("client_discoveries", [])]
        base_insight.goal_progress = [GoalProgress(**g) for g in analysis.get("goal_progress", [])]
        base_insight.coaching_presence = CoachingPresence(**analysis["coaching_presence"]) if analysis.get("coaching_presence") else None
        base_insight.powerful_questions = [PowerfulQuestion(**q) for q in analysis.get("powerful_questions", [])]
        base_insight.action_items = [ActionItem(**a) for a in analysis.get("action_items", [])]
        base_insight.emotional_shifts = [EmotionalShift(**e) for e in analysis.get("emotional_shifts", [])]
        base_insight.values_beliefs = [ValuesBeliefs(**v) for v in analysis.get("values_beliefs", [])]
        base_insight.communication_patterns = CommunicationPattern(**analysis["communication_patterns"]) if analysis.get("communication_patterns") else None
        
        # Set summary fields
        base_insight.session_summary = analysis.get("session_summary", "")
        base_insight.key_themes = analysis.get("key_themes", [])
        base_insight.overall_session_quality = analysis.get("overall_session_quality", "Average")
        
        # Set completion status
        base_insight.status = SessionInsightStatus.COMPLETED
        base_insight.completed_at = datetime.utcnow()
        
        # Add metadata
        base_insight.metadata = SessionMetadata(
            transcript_word_count=len(transcript_content.split()),
            ai_provider=settings.ai_provider,
            model_version=settings.ai_model,
            processing_time_seconds=0.0,  # Would be calculated
            analysis_confidence=0.85  # Could be derived from AI response
        )
        
        return base_insight