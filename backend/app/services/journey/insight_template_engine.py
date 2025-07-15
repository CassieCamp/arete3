"""
Insight Template Engine

This module provides the InsightTemplateEngine class for generating context-aware,
dynamic AI prompts for insight generation based on reflection type and user context.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import logging
from datetime import datetime


class BaseTemplate(ABC):
    """Base class for all insight generation templates."""
    
    @abstractmethod
    def generate_prompt(self, reflection: dict, user_profile: dict, context: dict) -> str:
        """Generate the AI prompt for this template type."""
        pass
    
    @abstractmethod
    def get_template_type(self) -> str:
        """Return the template type identifier."""
        pass


class CoachingSessionTemplate(BaseTemplate):
    """Template for generating insights from coaching session reflections."""
    
    def get_template_type(self) -> str:
        return "coaching_session"
    
    def generate_prompt(self, reflection: dict, user_profile: dict, context: dict) -> str:
        """Generate sophisticated coaching session insight prompt with enhanced context awareness."""
        
        user_name = user_profile.get('name', 'the user')
        user_role = user_profile.get('role', 'Client')
        experience_level = user_profile.get('experience_level', 'Not specified')
        focus_areas = user_profile.get('focus_areas', [])
        
        goals = context.get('active_goals', [])
        previous_insights = context.get('recent_insights', [])
        patterns = context.get('patterns', [])
        coaching_history = context.get('coaching_history', {})
        
        # Build comprehensive context sections
        goals_text = ""
        if goals:
            goals_text = f"\n\nACTIVE GOALS & OBJECTIVES:\n" + "\n".join([
                f"- {goal.get('title', 'Untitled goal')}: {goal.get('description', 'No description')[:100]}..."
                if goal.get('description') else f"- {goal.get('title', 'Untitled goal')}"
                for goal in goals[:5]
            ])
        
        previous_context = ""
        if previous_insights:
            previous_context = f"\n\nRECENT INSIGHTS CONTEXT (for continuity):\n" + "\n".join([
                f"- {insight.get('title', 'Untitled')}: {insight.get('summary', '')[:80]}..."
                for insight in previous_insights[:3]
            ])
        
        patterns_text = ""
        if patterns:
            patterns_text = f"\n\nIDENTIFIED PATTERNS:\n" + "\n".join([
                f"- {pattern.get('description', pattern)}" for pattern in patterns[:3]
            ])
        
        focus_areas_text = ""
        if focus_areas:
            focus_areas_text = f"\n\nFOCUS AREAS: {', '.join(focus_areas)}"
        
        coaching_context = ""
        if coaching_history:
            session_count = coaching_history.get('total_sessions', 0)
            recent_themes = coaching_history.get('recent_themes', [])
            coaching_context = f"\n\nCOACHING CONTEXT:\n- Total Sessions: {session_count}\n- Recent Themes: {', '.join(recent_themes[:3])}"
        
        prompt = f"""You are an expert coaching insights analyst with deep expertise in human development, behavioral psychology, and transformational coaching methodologies. Your role is to analyze coaching session reflections and generate profound, actionable insights that accelerate personal and professional growth.

COMPREHENSIVE USER PROFILE:
- Name: {user_name}
- Role: {user_role}
- Experience Level: {experience_level}{focus_areas_text}{goals_text}{previous_context}{patterns_text}{coaching_context}

REFLECTION TO ANALYZE:
Session Type: {reflection.get('type', 'coaching_session')}
Session Title: {reflection.get('title', 'Coaching Session')}
Content: {reflection.get('content', '')}
Session Date: {reflection.get('created_at', 'Not specified')}
Duration: {reflection.get('duration', 'Not specified')}
Key Themes Mentioned: {reflection.get('themes', [])}
Emotional Tone: {reflection.get('emotional_tone', 'Not specified')}

SOPHISTICATED ANALYSIS FRAMEWORK:
1. **Pattern Recognition**: Identify recurring themes, behavioral patterns, and growth trajectories
2. **Breakthrough Identification**: Detect moments of significant realization, mindset shifts, or "aha" moments
3. **Goal Alignment Analysis**: Assess how session content aligns with stated objectives and development areas
4. **Emotional Intelligence Insights**: Recognize emotional patterns, triggers, and emotional growth opportunities
5. **Action-Oriented Synthesis**: Generate specific, measurable next steps that build on session momentum
6. **Systemic Connections**: Link insights to broader life/career contexts and long-term development
7. **Resistance & Obstacle Analysis**: Identify potential barriers and strategies to overcome them

RESPONSE FORMAT - Generate exactly 3-5 insights in this JSON structure:
{{
    "insights": [
        {{
            "type": "breakthrough|pattern_recognition|goal_alignment|emotional_intelligence|action_catalyst|systemic_connection",
            "title": "Compelling, specific insight title (max 60 characters)",
            "summary": "Concise 2-3 sentence summary highlighting the core insight and its significance",
            "details": "Comprehensive analysis with specific examples from the reflection, psychological context, and developmental implications",
            "actionable_steps": [
                "Specific, measurable action step with timeline",
                "Follow-up action that builds on the first",
                "Optional third step for deeper integration"
            ],
            "confidence_score": 0.75,
            "impact_potential": "high|medium|low",
            "tags": ["specific", "relevant", "categorization", "tags"],
            "goal_connections": ["goal_id_1", "goal_id_2"],
            "follow_up_questions": [
                "Thought-provoking question to deepen exploration",
                "Optional second question for continued reflection"
            ]
        }}
    ],
    "session_summary": {{
        "key_themes": ["theme1", "theme2", "theme3"],
        "emotional_journey": "Brief description of emotional arc during session",
        "breakthrough_moments": ["moment1", "moment2"],
        "recommended_focus": "Primary area for continued development"
    }}
}}

QUALITY STANDARDS - Ensure insights are:
✓ **Contextually Rich**: Deeply connected to {user_name}'s specific situation, goals, and development stage
✓ **Psychologically Informed**: Grounded in coaching psychology and human development principles
✓ **Actionably Specific**: Include concrete steps with clear implementation pathways
✓ **Growth-Oriented**: Focus on expansion, capability building, and positive transformation
✓ **Authentically Derived**: Directly extracted from and supported by the reflection content
✓ **Systemically Aware**: Consider broader life context and interconnected development areas

Analyze the reflection now and provide the insights in the specified JSON format, ensuring each insight catalyzes meaningful growth for {user_name}."""
        
        return prompt.strip()


class DocumentInsightTemplate(BaseTemplate):
    """Template for generating insights from document analysis reflections."""
    
    def get_template_type(self) -> str:
        return "document_analysis"
    
    def generate_prompt(self, reflection: dict, user_profile: dict, context: dict) -> str:
        """Generate sophisticated document analysis insight prompt with enhanced learning synthesis."""
        
        user_name = user_profile.get('name', 'the user')
        user_role = user_profile.get('role', 'Client')
        focus_areas = user_profile.get('focus_areas', ['Personal Development'])
        learning_style = user_profile.get('learning_style', 'Not specified')
        
        document_info = context.get('document_metadata', {})
        goals = context.get('active_goals', [])
        related_documents = context.get('related_documents', [])
        learning_history = context.get('learning_history', {})
        
        # Build comprehensive document context
        doc_context = ""
        if document_info:
            doc_context = f"""
DOCUMENT CONTEXT:
- Title: {document_info.get('title', 'Unknown')}
- Type: {document_info.get('type', 'Unknown')}
- Author: {document_info.get('author', 'Unknown')}
- Upload Date: {document_info.get('upload_date', 'Unknown')}
- Length: {document_info.get('page_count', 'Unknown')} pages
- Source: {document_info.get('source', 'User upload')}"""
        
        goals_text = ""
        if goals:
            goals_text = f"\n\nLEARNING OBJECTIVES & GOALS:\n" + "\n".join([
                f"- {goal.get('title', 'Untitled goal')}: {goal.get('description', 'No description')[:100]}..."
                if goal.get('description') else f"- {goal.get('title', 'Untitled goal')}"
                for goal in goals[:5]
            ])
        
        related_docs_text = ""
        if related_documents:
            related_docs_text = f"\n\nRELATED LEARNING MATERIALS:\n" + "\n".join([
                f"- {doc.get('title', 'Unknown')}" for doc in related_documents[:3]
            ])
        
        learning_context = ""
        if learning_history:
            recent_topics = learning_history.get('recent_topics', [])
            learning_patterns = learning_history.get('patterns', [])
            learning_context = f"\n\nLEARNING CONTEXT:\n- Recent Topics: {', '.join(recent_topics[:3])}\n- Learning Patterns: {', '.join(learning_patterns[:2])}"
        
        prompt = f"""You are an expert learning analyst and knowledge synthesis specialist with deep expertise in adult learning theory, knowledge management, and transformational education. Your role is to analyze document reflections and generate profound insights that accelerate learning integration and practical application.

COMPREHENSIVE LEARNER PROFILE:
- Name: {user_name}
- Role: {user_role}
- Focus Areas: {', '.join(focus_areas)}
- Learning Style: {learning_style}{doc_context}{goals_text}{related_docs_text}{learning_context}

DOCUMENT REFLECTION TO ANALYZE:
Reflection Type: {reflection.get('type', 'document_analysis')}
Document Title: {reflection.get('document_title', 'Unknown Document')}
User's Reflection: {reflection.get('content', '')}
Key Themes Identified: {reflection.get('themes', [])}
Personal Notes: {reflection.get('user_notes', '')}
Reading Context: {reflection.get('reading_context', 'Not specified')}
Completion Status: {reflection.get('completion_status', 'Not specified')}
Difficulty Level: {reflection.get('difficulty_level', 'Not specified')}

ADVANCED ANALYSIS FRAMEWORK:
1. **Knowledge Synthesis**: Identify core concepts, frameworks, and mental models from the document
2. **Personal Relevance Mapping**: Connect document insights to user's specific context and challenges
3. **Application Pathway Analysis**: Determine practical implementation strategies and real-world applications
4. **Paradigm Shift Detection**: Recognize new perspectives or worldview changes triggered by the content
5. **Knowledge Gap Identification**: Highlight areas for deeper exploration or complementary learning
6. **Integration Opportunities**: Find connections with existing knowledge and previous learning
7. **Behavioral Change Catalysts**: Identify insights that could drive meaningful behavior modification

RESPONSE FORMAT - Generate exactly 3-5 insights in this JSON structure:
{{
    "insights": [
        {{
            "type": "knowledge_synthesis|practical_application|paradigm_shift|skill_development|behavioral_catalyst|integration_opportunity",
            "title": "Compelling, specific insight title (max 60 characters)",
            "summary": "Concise 2-3 sentence summary connecting document content to personal growth and application",
            "details": "Comprehensive analysis linking document concepts to user's context, with specific examples and implementation considerations",
            "actionable_steps": [
                "Specific, measurable implementation step with timeline",
                "Follow-up action that deepens understanding or application",
                "Optional integration step connecting to broader goals"
            ],
            "confidence_score": 0.80,
            "application_difficulty": "low|medium|high",
            "tags": ["document_topic", "skill_area", "application_context"],
            "source_references": [
                "Specific quote or concept from the document",
                "Key framework or model referenced"
            ],
            "goal_connections": ["goal_id_1", "goal_id_2"],
            "recommended_resources": [
                "Complementary resource for deeper learning",
                "Tool or method for practical application"
            ],
            "reflection_prompts": [
                "Question to deepen understanding of the concept",
                "Prompt for personal application planning"
            ]
        }}
    ],
    "learning_summary": {{
        "key_concepts": ["concept1", "concept2", "concept3"],
        "practical_applications": ["application1", "application2"],
        "knowledge_gaps": ["gap1", "gap2"],
        "next_learning_priorities": ["priority1", "priority2"],
        "integration_opportunities": ["opportunity1", "opportunity2"]
    }}
}}

QUALITY STANDARDS - Ensure insights are:
✓ **Pedagogically Sound**: Grounded in adult learning principles and knowledge transfer theory
✓ **Contextually Relevant**: Specifically tailored to {user_name}'s role, goals, and development needs
✓ **Practically Actionable**: Include concrete implementation steps with clear success metrics
✓ **Intellectually Rigorous**: Demonstrate deep understanding of document content and its implications
✓ **Synthetically Rich**: Connect new learning with existing knowledge and broader development goals
✓ **Transformationally Oriented**: Focus on insights that can drive meaningful change and growth

Analyze the document reflection now and provide the insights in the specified JSON format, ensuring each insight maximizes learning integration and practical application for {user_name}."""
        
        return prompt.strip()


class InsightTemplateEngine:
    """
    Main engine for generating context-aware AI prompts for insight generation.
    
    This class orchestrates the template selection and prompt generation process
    based on reflection type and user context.
    """
    
    def __init__(self, user_context_service=None, goal_service=None):
        """
        Initialize the InsightTemplateEngine.
        
        Args:
            user_context_service: Service for retrieving user context data
            goal_service: Service for retrieving user goals
        """
        self.user_context_service = user_context_service
        self.goal_service = goal_service
        
        # Initialize available templates
        self.templates = {
            'coaching_session': CoachingSessionTemplate(),
            'document_analysis': DocumentInsightTemplate(),
        }
    
    def generate_insights(self, reflection: dict) -> List[dict]:
        """
        Main method to orchestrate the insight generation process.
        
        Args:
            reflection: The reflection data to analyze
            
        Returns:
            List of generated insights
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Starting insight generation for reflection: {reflection.get('id', 'unknown')}")
        
        try:
            # Extract reflection type
            reflection_type = reflection.get('type', 'coaching_session')
            logger.info(f"Processing reflection type: {reflection_type}")
            
            # Get user profile (placeholder for now)
            user_profile = self._get_user_profile(reflection.get('user_id'))
            
            # Select appropriate template
            template = self._select_template(reflection_type, user_profile)
            logger.info(f"Selected template: {template.get_template_type()}")
            
            # Extract patterns and context
            context = self._extract_patterns(reflection, user_profile)
            
            # Generate prompt using selected template
            prompt = template.generate_prompt(reflection, user_profile, context)
            logger.info(f"Generated prompt length: {len(prompt)} characters")
            
            # Call AI service to generate insights (returns JSON string)
            raw_insights_json = self._call_ai_service(prompt)
            
            # Validate and enhance insights (parses JSON and validates)
            validated_insights = self._validate_and_enhance(raw_insights_json, reflection, user_profile)
            
            logger.info(f"Successfully generated {len(validated_insights)} insights")
            return validated_insights
            
        except Exception as e:
            logger.error(f"Error in insight generation: {e}")
            # Return fallback insight on any unexpected error
            return self._create_fallback_insight(reflection, f"Unexpected error: {str(e)}")
    
    def _select_template(self, reflection_type: str, user_profile: dict) -> BaseTemplate:
        """
        Select the appropriate template based on reflection type and user context.
        
        Args:
            reflection_type: Type of reflection (e.g., 'coaching_session', 'document_analysis')
            user_profile: User profile information
            
        Returns:
            Selected template instance
        """
        # Default to coaching session template if type not found
        template_key = reflection_type if reflection_type in self.templates else 'coaching_session'
        
        return self.templates[template_key]
    
    def _get_user_profile(self, user_id: str) -> dict:
        """
        Retrieve user profile information.
        
        Args:
            user_id: User identifier
            
        Returns:
            User profile dictionary
        """
        # Placeholder implementation
        # In production, this would call the user_context_service
        return {
            'name': 'User',
            'role': 'Client',
            'experience_level': 'Intermediate',
            'focus_areas': ['Personal Development', 'Goal Achievement']
        }
    
    def _extract_patterns(self, reflection: dict, user_profile: dict) -> dict:
        """
        Extract patterns and context from reflection and user data.
        
        Args:
            reflection: Reflection data
            user_profile: User profile information
            
        Returns:
            Context dictionary with patterns and relevant data
        """
        # Placeholder implementation
        # In production, this would analyze patterns and retrieve context
        context = {
            'active_goals': [],
            'recent_insights': [],
            'document_metadata': {},
            'patterns': []
        }
        
        # If it's a document analysis, extract document metadata
        if reflection.get('type') == 'document_analysis':
            context['document_metadata'] = {
                'title': reflection.get('document_title', 'Unknown Document'),
                'type': reflection.get('document_type', 'Unknown'),
                'upload_date': reflection.get('created_at', 'Unknown')
            }
        
        return context
    
    def _call_ai_service(self, prompt: str) -> str:
        """
        Call the AI service to generate insights based on the prompt.
        
        Args:
            prompt: Generated prompt for AI analysis
            
        Returns:
            Raw JSON string response from AI service
        """
        logger = logging.getLogger(__name__)
        logger.info("Calling AI service for insight generation")
        
        # Determine response type based on prompt content
        if "coaching session" in prompt.lower() or "coaching_session" in prompt:
            # Mock coaching session response
            mock_response = {
                "insights": [
                    {
                        "type": "breakthrough",
                        "title": "Communication Pattern Recognition",
                        "summary": "Identified a recurring pattern in communication style that impacts professional relationships. This breakthrough reveals how active listening techniques can transform interpersonal dynamics.",
                        "details": "The reflection shows a significant shift in awareness about communication patterns, particularly around interrupting and not fully processing others' perspectives before responding. This pattern appears to stem from anxiety about being heard and understood, but paradoxically creates barriers to genuine connection.",
                        "actionable_steps": [
                            "Practice the 3-second pause technique before responding in conversations this week",
                            "Implement daily reflection on one meaningful conversation to assess listening quality",
                            "Schedule follow-up coaching session to explore underlying anxiety patterns"
                        ],
                        "confidence_score": 0.88,
                        "impact_potential": "high",
                        "tags": ["communication", "self_awareness", "interpersonal_skills", "breakthrough"],
                        "goal_connections": ["goal_1", "goal_2"],
                        "follow_up_questions": [
                            "What specific situations trigger your tendency to interrupt or rush responses?",
                            "How might this new awareness change your approach to difficult conversations?"
                        ]
                    },
                    {
                        "type": "action_catalyst",
                        "title": "Leadership Presence Development",
                        "summary": "The session revealed readiness to step into more visible leadership roles. Key insight around leveraging authentic communication style as a leadership strength.",
                        "details": "The reflection demonstrates growing confidence in personal leadership capabilities, with specific examples of successful team interactions. The user is ready to move from informal influence to formal leadership responsibilities.",
                        "actionable_steps": [
                            "Volunteer to lead next team project or initiative within 2 weeks",
                            "Schedule conversation with manager about leadership development opportunities",
                            "Begin documenting leadership wins and challenges in weekly journal"
                        ],
                        "confidence_score": 0.82,
                        "impact_potential": "high",
                        "tags": ["leadership", "career_development", "confidence", "action_oriented"],
                        "goal_connections": ["goal_3"],
                        "follow_up_questions": [
                            "What leadership opportunity feels most aligned with your current strengths?",
                            "How can you leverage your authentic communication style in leadership contexts?"
                        ]
                    },
                    {
                        "type": "emotional_intelligence",
                        "title": "Emotional Regulation Under Pressure",
                        "summary": "Developed new strategies for managing stress responses in high-pressure situations. Shows improved emotional awareness and regulation techniques.",
                        "details": "The reflection indicates significant progress in recognizing emotional triggers before they escalate, particularly in deadline-driven environments. The user has successfully implemented breathing techniques and cognitive reframing strategies.",
                        "actionable_steps": [
                            "Create a personalized stress response toolkit with 3-5 go-to techniques",
                            "Practice daily mindfulness meditation for 10 minutes to build emotional awareness",
                            "Implement weekly stress level check-ins to track progress"
                        ],
                        "confidence_score": 0.79,
                        "impact_potential": "medium",
                        "tags": ["emotional_intelligence", "stress_management", "mindfulness", "self_regulation"],
                        "goal_connections": ["goal_1"],
                        "follow_up_questions": [
                            "Which emotional regulation technique has been most effective for you so far?",
                            "How might you share these strategies with team members who face similar pressures?"
                        ]
                    }
                ],
                "session_summary": {
                    "key_themes": ["communication_improvement", "leadership_readiness", "emotional_regulation"],
                    "emotional_journey": "Started with frustration about communication challenges, moved through recognition and acceptance, ending with excitement about growth opportunities",
                    "breakthrough_moments": ["Recognition of interrupting pattern", "Confidence in leadership capabilities"],
                    "recommended_focus": "Continue developing active listening skills while exploring leadership opportunities"
                }
            }
        else:
            # Mock document analysis response
            mock_response = {
                "insights": [
                    {
                        "type": "knowledge_synthesis",
                        "title": "Systems Thinking Framework Integration",
                        "summary": "Successfully synthesized key systems thinking concepts from the document. Ready to apply holistic problem-solving approaches to current challenges.",
                        "details": "The reflection demonstrates deep understanding of interconnected systems and feedback loops. The user has connected these concepts to their specific work context, particularly around organizational change initiatives.",
                        "actionable_steps": [
                            "Map current project challenges using systems thinking framework within 1 week",
                            "Identify 3 key leverage points for maximum impact in ongoing initiatives",
                            "Share systems thinking insights with team in next planning meeting"
                        ],
                        "confidence_score": 0.85,
                        "application_difficulty": "medium",
                        "tags": ["systems_thinking", "problem_solving", "organizational_change"],
                        "source_references": [
                            "Leverage points in systems thinking hierarchy",
                            "Feedback loop identification methodology"
                        ],
                        "goal_connections": ["goal_2", "goal_4"],
                        "recommended_resources": [
                            "Systems Thinking Workbook by Linda Booth Sweeney",
                            "Kumu.io for systems mapping visualization"
                        ],
                        "reflection_prompts": [
                            "What systems patterns do you recognize in your current work environment?",
                            "How might systems thinking change your approach to team collaboration?"
                        ]
                    },
                    {
                        "type": "practical_application",
                        "title": "Strategic Planning Implementation",
                        "summary": "Document insights provide clear framework for improving strategic planning processes. Ready to implement structured approach to goal setting and execution.",
                        "details": "The reflection shows strong grasp of strategic planning principles and eagerness to apply them. User has identified specific areas where current planning processes could be enhanced using document frameworks.",
                        "actionable_steps": [
                            "Redesign quarterly planning process using new strategic framework by month-end",
                            "Create template for team goal-setting sessions based on document methodology",
                            "Schedule pilot strategic planning session with immediate team within 3 weeks"
                        ],
                        "confidence_score": 0.81,
                        "application_difficulty": "low",
                        "tags": ["strategic_planning", "goal_setting", "process_improvement"],
                        "source_references": [
                            "SMART goals evolution to CLEAR framework",
                            "Quarterly review and adjustment methodology"
                        ],
                        "goal_connections": ["goal_1", "goal_3"],
                        "recommended_resources": [
                            "Strategic Planning Template Library",
                            "OKR implementation guide"
                        ],
                        "reflection_prompts": [
                            "How can you adapt these planning frameworks to your team's specific needs?",
                            "What metrics will help you measure the effectiveness of your new planning approach?"
                        ]
                    },
                    {
                        "type": "paradigm_shift",
                        "title": "Growth Mindset Integration",
                        "summary": "Document content has catalyzed a fundamental shift from fixed to growth mindset thinking. This paradigm change opens new possibilities for personal and professional development.",
                        "details": "The reflection reveals a significant transformation in how challenges and failures are perceived. Instead of viewing setbacks as evidence of limitations, the user now sees them as learning opportunities and stepping stones to mastery.",
                        "actionable_steps": [
                            "Reframe one current challenge using growth mindset language this week",
                            "Create a 'learning from failure' journal to track insights from setbacks",
                            "Share growth mindset concepts with team members to create supportive environment"
                        ],
                        "confidence_score": 0.77,
                        "application_difficulty": "medium",
                        "tags": ["mindset", "personal_development", "resilience", "learning"],
                        "source_references": [
                            "Fixed vs. growth mindset characteristics",
                            "Neuroplasticity and learning potential"
                        ],
                        "goal_connections": ["goal_2"],
                        "recommended_resources": [
                            "Mindset: The New Psychology of Success by Carol Dweck",
                            "Growth mindset assessment tools"
                        ],
                        "reflection_prompts": [
                            "What specific beliefs about your abilities are shifting as a result of this new perspective?",
                            "How might embracing a growth mindset change your approach to upcoming challenges?"
                        ]
                    }
                ],
                "learning_summary": {
                    "key_concepts": ["systems_thinking", "strategic_planning", "growth_mindset"],
                    "practical_applications": ["process_mapping", "goal_framework_implementation", "mindset_reframing"],
                    "knowledge_gaps": ["advanced_systems_modeling", "change_management_techniques"],
                    "next_learning_priorities": ["leadership_in_complex_systems", "organizational_psychology"],
                    "integration_opportunities": ["team_planning_sessions", "personal_development_coaching"]
                }
            }
        
        # Convert to JSON string to simulate API response
        return json.dumps(mock_response)
    
    def _validate_and_enhance(self, raw_insights_json: str, reflection: dict, user_profile: dict) -> List[dict]:
        """
        Validate and enhance the generated insights from JSON string response.
        
        Args:
            raw_insights_json: Raw JSON string response from AI service
            reflection: Original reflection data
            user_profile: User profile information
            
        Returns:
            Validated and enhanced insights list
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Parse JSON response
            raw_insights = json.loads(raw_insights_json)
            logger.info("Successfully parsed AI service JSON response")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI service response as JSON: {e}")
            # Return fallback insight on JSON parse error
            return [{
                'type': 'error',
                'title': 'Processing Error',
                'summary': 'Unable to process AI response due to formatting issues.',
                'details': 'The AI service returned an invalid response format. Please try again.',
                'actionable_steps': ['Contact support if this error persists'],
                'confidence_score': 0.0,
                'tags': ['error', 'system_issue'],
                'reflection_id': reflection.get('id'),
                'user_id': reflection.get('user_id'),
                'generated_at': datetime.utcnow().isoformat(),
                'template_type': reflection.get('type', 'coaching_session')
            }]
        
        # Validate response structure
        if not isinstance(raw_insights, dict):
            logger.error("AI response is not a dictionary")
            return self._create_fallback_insight(reflection, "Invalid response structure")
        
        if 'insights' not in raw_insights:
            logger.error("AI response missing 'insights' key")
            return self._create_fallback_insight(reflection, "Missing insights in response")
        
        insights = raw_insights.get('insights', [])
        
        if not isinstance(insights, list):
            logger.error("Insights field is not a list")
            return self._create_fallback_insight(reflection, "Invalid insights format")
        
        if len(insights) == 0:
            logger.warning("AI service returned empty insights list")
            return self._create_fallback_insight(reflection, "No insights generated")
        
        # Validate and enhance each insight
        validated_insights = []
        current_time = datetime.utcnow().isoformat()
        
        for i, insight in enumerate(insights):
            try:
                # Validate required fields
                required_fields = ['type', 'title', 'summary', 'details', 'actionable_steps', 'confidence_score']
                for field in required_fields:
                    if field not in insight:
                        logger.warning(f"Insight {i} missing required field: {field}")
                        insight[field] = self._get_default_value(field)
                
                # Validate data types and constraints
                insight['confidence_score'] = max(0.0, min(1.0, float(insight.get('confidence_score', 0.5))))
                
                if not isinstance(insight.get('actionable_steps'), list):
                    insight['actionable_steps'] = [str(insight.get('actionable_steps', 'No action steps provided'))]
                
                if not isinstance(insight.get('tags'), list):
                    insight['tags'] = []
                
                # Enhance with metadata
                insight['reflection_id'] = reflection.get('id')
                insight['user_id'] = reflection.get('user_id')
                insight['generated_at'] = current_time
                insight['template_type'] = reflection.get('type', 'coaching_session')
                insight['insight_id'] = f"{reflection.get('id', 'unknown')}_{i}_{int(datetime.utcnow().timestamp())}"
                
                # Add processing metadata
                insight['processing_metadata'] = {
                    'ai_model': 'mock_model_v1',
                    'template_version': '2.0',
                    'processing_time': current_time,
                    'validation_passed': True
                }
                
                validated_insights.append(insight)
                
            except Exception as e:
                logger.error(f"Error validating insight {i}: {e}")
                # Skip invalid insights but continue processing others
                continue
        
        if len(validated_insights) == 0:
            logger.error("No valid insights after validation")
            return self._create_fallback_insight(reflection, "All insights failed validation")
        
        logger.info(f"Successfully validated {len(validated_insights)} insights")
        return validated_insights
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing insight fields."""
        defaults = {
            'type': 'general',
            'title': 'Generated Insight',
            'summary': 'An insight was generated from your reflection.',
            'details': 'Additional details were not provided.',
            'actionable_steps': ['Review your reflection for key takeaways'],
            'confidence_score': 0.5,
            'tags': ['general']
        }
        return defaults.get(field, '')
    
    def _create_fallback_insight(self, reflection: dict, error_message: str) -> List[dict]:
        """Create a fallback insight when AI processing fails."""
        return [{
            'type': 'fallback',
            'title': 'Reflection Processed',
            'summary': f'Your reflection has been recorded. {error_message}',
            'details': 'While we encountered an issue generating detailed insights, your reflection is valuable and has been saved for future reference.',
            'actionable_steps': [
                'Review your reflection manually for key insights',
                'Consider discussing your reflection with a coach or mentor',
                'Try submitting another reflection to generate new insights'
            ],
            'confidence_score': 0.3,
            'tags': ['fallback', 'system_generated'],
            'reflection_id': reflection.get('id'),
            'user_id': reflection.get('user_id'),
            'generated_at': datetime.utcnow().isoformat(),
            'template_type': reflection.get('type', 'coaching_session'),
            'processing_metadata': {
                'ai_model': 'fallback',
                'template_version': '2.0',
                'processing_time': datetime.utcnow().isoformat(),
                'validation_passed': False,
                'error_message': error_message
            }
        }]
    
    def add_template(self, template_type: str, template: BaseTemplate):
        """
        Add a new template to the engine.
        
        Args:
            template_type: Identifier for the template type
            template: Template instance
        """
        self.templates[template_type] = template
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template types.
        
        Returns:
            List of template type identifiers
        """
        return list(self.templates.keys())


async def process_reflection_ai(reflection_id: str) -> Dict[str, Any]:
    """
    Background task to process reflection and generate insights using the consolidated template engine.
    
    Args:
        reflection_id: ID of the reflection to process
        
    Returns:
        Dict[str, Any]: Processing results including generated insights
    """
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting AI processing for reflection: {reflection_id}")
    
    start_time = datetime.utcnow()
    
    try:
        # Get reflection data (placeholder for actual repository call)
        reflection = await _get_reflection_data(reflection_id)
        
        if not reflection:
            raise ValueError(f"Reflection not found: {reflection_id}")
        
        # Initialize InsightTemplateEngine with mocked dependencies
        template_engine = InsightTemplateEngine(
            user_context_service=None,  # Will be integrated later
            goal_service=None  # Will be integrated later
        )
        
        # Generate insights using the consolidated template engine
        insights = template_engine.generate_insights(reflection)
        
        # Calculate processing duration
        processing_duration = (datetime.utcnow() - start_time).total_seconds()
        
        # Compile results
        results = {
            'reflection_id': reflection_id,
            'status': 'completed',
            'insights_generated': len(insights),
            'processing_duration': processing_duration,
            'insights': insights,
            'processed_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"AI processing completed for reflection {reflection_id}: {len(insights)} insights generated in {processing_duration:.2f}s")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in AI processing for reflection {reflection_id}: {e}")
        
        # Return error result
        return {
            'reflection_id': reflection_id,
            'status': 'failed',
            'error': str(e),
            'processing_duration': (datetime.utcnow() - start_time).total_seconds(),
            'processed_at': datetime.utcnow().isoformat()
        }


async def _get_reflection_data(reflection_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve reflection data from repository (mocked for now).
    
    Args:
        reflection_id: ID of the reflection to retrieve
        
    Returns:
        Optional[Dict[str, Any]]: Reflection data or None if not found
    """
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Retrieving reflection data for ID: {reflection_id}")
    
    # Mock reflection data
    return {
        'id': reflection_id,
        'user_id': 'mock_user_id',
        'type': 'coaching_session',
        'title': 'Weekly Coaching Session Reflection',
        'content': 'Today I had a breakthrough in understanding my communication patterns...',
        'created_at': datetime.utcnow().isoformat(),
        'themes': ['communication', 'self_awareness'],
        'user_notes': 'Need to focus more on active listening'
    }