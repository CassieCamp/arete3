"""
Insight Template Engine

This module provides the InsightTemplateEngine class for generating context-aware,
dynamic AI prompts for insight generation based on reflection type and user context.
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod


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
        """Generate coaching session insight prompt."""
        
        user_name = user_profile.get('name', 'the user')
        goals = context.get('active_goals', [])
        previous_insights = context.get('recent_insights', [])
        
        goals_text = ""
        if goals:
            goals_text = f"\n\nActive Goals:\n" + "\n".join([f"- {goal.get('title', 'Untitled goal')}" for goal in goals])
        
        previous_context = ""
        if previous_insights:
            previous_context = f"\n\nRecent Insights Context:\n" + "\n".join([f"- {insight.get('summary', '')}" for insight in previous_insights[:3]])
        
        prompt = f"""
You are an expert coaching insights analyst. Analyze the following coaching session reflection and generate actionable insights.

USER PROFILE:
- Name: {user_name}
- Role: {user_profile.get('role', 'Client')}
- Experience Level: {user_profile.get('experience_level', 'Not specified')}
{goals_text}
{previous_context}

REFLECTION TO ANALYZE:
Type: {reflection.get('type', 'coaching_session')}
Content: {reflection.get('content', '')}
Timestamp: {reflection.get('created_at', 'Not specified')}

ANALYSIS REQUIREMENTS:
1. Identify key themes and patterns in the reflection
2. Extract actionable insights that align with the user's goals
3. Highlight breakthrough moments or significant realizations
4. Suggest specific next steps or areas for exploration
5. Note any emotional or mindset shifts mentioned

RESPONSE FORMAT:
Generate exactly 3-5 insights in the following JSON format:
{{
    "insights": [
        {{
            "type": "breakthrough|pattern|action_item|emotional_shift",
            "title": "Clear, compelling insight title",
            "summary": "2-3 sentence summary of the insight",
            "details": "Detailed explanation with specific examples from the reflection",
            "actionable_steps": ["Specific action step 1", "Specific action step 2"],
            "confidence_score": 0.85,
            "tags": ["relevant", "tags", "for", "categorization"]
        }}
    ]
}}

Focus on insights that are:
- Directly derived from the reflection content
- Actionable and specific to {user_name}'s situation
- Aligned with their stated goals and development areas
- Supportive of their growth journey

Analyze the reflection now and provide the insights in the specified JSON format.
"""
        return prompt.strip()


class DocumentInsightTemplate(BaseTemplate):
    """Template for generating insights from document analysis reflections."""
    
    def get_template_type(self) -> str:
        return "document_analysis"
    
    def generate_prompt(self, reflection: dict, user_profile: dict, context: dict) -> str:
        """Generate document analysis insight prompt."""
        
        user_name = user_profile.get('name', 'the user')
        document_info = context.get('document_metadata', {})
        goals = context.get('active_goals', [])
        
        doc_context = ""
        if document_info:
            doc_context = f"\n\nDocument Context:\n- Title: {document_info.get('title', 'Unknown')}\n- Type: {document_info.get('type', 'Unknown')}\n- Upload Date: {document_info.get('upload_date', 'Unknown')}"
        
        goals_text = ""
        if goals:
            goals_text = f"\n\nUser's Active Goals:\n" + "\n".join([f"- {goal.get('title', 'Untitled goal')}" for goal in goals])
        
        prompt = f"""
You are an expert document analysis and insight generation specialist. Analyze the following document reflection and extract meaningful insights.

USER PROFILE:
- Name: {user_name}
- Role: {user_profile.get('role', 'Client')}
- Focus Areas: {user_profile.get('focus_areas', ['Personal Development'])}
{doc_context}
{goals_text}

DOCUMENT REFLECTION TO ANALYZE:
Type: {reflection.get('type', 'document_analysis')}
Content: {reflection.get('content', '')}
Key Themes: {reflection.get('themes', [])}
User Notes: {reflection.get('user_notes', '')}

ANALYSIS REQUIREMENTS:
1. Extract key learnings and takeaways from the document
2. Identify how the content relates to the user's goals and development areas
3. Highlight practical applications and implementation strategies
4. Note any paradigm shifts or new perspectives gained
5. Suggest follow-up actions or related resources

RESPONSE FORMAT:
Generate exactly 3-5 insights in the following JSON format:
{{
    "insights": [
        {{
            "type": "learning|application|perspective_shift|resource_connection",
            "title": "Clear, actionable insight title",
            "summary": "2-3 sentence summary connecting document content to user's journey",
            "details": "Detailed explanation with specific references to document content",
            "actionable_steps": ["Specific implementation step 1", "Specific implementation step 2"],
            "confidence_score": 0.80,
            "tags": ["document_type", "relevant", "topic", "tags"],
            "source_references": ["Specific quotes or sections from the document"]
        }}
    ]
}}

Focus on insights that are:
- Directly connected to the document content and user's reflection
- Practically applicable to {user_name}'s current situation
- Aligned with their learning objectives and goals
- Actionable with clear next steps

Analyze the document reflection now and provide the insights in the specified JSON format.
"""
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
        # Extract reflection type
        reflection_type = reflection.get('type', 'coaching_session')
        
        # Get user profile (placeholder for now)
        user_profile = self._get_user_profile(reflection.get('user_id'))
        
        # Select appropriate template
        template = self._select_template(reflection_type, user_profile)
        
        # Extract patterns and context
        context = self._extract_patterns(reflection, user_profile)
        
        # Generate prompt using selected template
        prompt = template.generate_prompt(reflection, user_profile, context)
        
        # Call AI service to generate insights
        raw_insights = self._call_ai_service(prompt)
        
        # Validate and enhance insights
        validated_insights = self._validate_and_enhance(raw_insights, reflection, user_profile)
        
        return validated_insights
    
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
    
    def _call_ai_service(self, prompt: str) -> dict:
        """
        Call the AI service to generate insights based on the prompt.
        
        Args:
            prompt: Generated prompt for AI analysis
            
        Returns:
            Raw insights from AI service
        """
        # Placeholder implementation
        # In production, this would call the actual AI service
        return {
            'insights': [
                {
                    'type': 'pattern',
                    'title': 'Sample Insight',
                    'summary': 'This is a sample insight generated from the template.',
                    'details': 'Detailed analysis would be provided by the AI service.',
                    'actionable_steps': ['Sample action step'],
                    'confidence_score': 0.75,
                    'tags': ['sample', 'placeholder']
                }
            ]
        }
    
    def _validate_and_enhance(self, raw_insights: dict, reflection: dict, user_profile: dict) -> List[dict]:
        """
        Validate and enhance the generated insights.
        
        Args:
            raw_insights: Raw insights from AI service
            reflection: Original reflection data
            user_profile: User profile information
            
        Returns:
            Validated and enhanced insights list
        """
        # Placeholder implementation
        # In production, this would validate structure, enhance with metadata, etc.
        insights = raw_insights.get('insights', [])
        
        # Add metadata to each insight
        for insight in insights:
            insight['reflection_id'] = reflection.get('id')
            insight['user_id'] = reflection.get('user_id')
            insight['generated_at'] = reflection.get('created_at')
            insight['template_type'] = reflection.get('type', 'coaching_session')
        
        return insights
    
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