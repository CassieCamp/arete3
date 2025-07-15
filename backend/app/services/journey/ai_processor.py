"""
AI Processing Service for Journey System

This module contains AI processing functions for analyzing reflection documents
and generating categorized insights.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.services.ai_service import AIService
from app.models.journey.reflection import DocumentAnalysis
from app.models.journey.enums import CategoryType

logger = logging.getLogger(__name__)

# Map the 4 specified categories to our CategoryType enum
INSIGHT_CATEGORIES = {
    "Understanding Myself": [CategoryType.PERSONAL_GROWTH, CategoryType.VALUES, CategoryType.MINDSET],
    "Navigating Relationships": [CategoryType.RELATIONSHIPS, CategoryType.COMMUNICATION, CategoryType.LEADERSHIP],
    "Optimizing Performance": [CategoryType.GOALS_ACHIEVEMENT, CategoryType.HABITS, CategoryType.LEARNING],
    "Making Progress": [CategoryType.CHALLENGES, CategoryType.CELEBRATIONS, CategoryType.PURPOSE]
}

async def analyze_text_for_insights(text: str) -> DocumentAnalysis:
    """
    Analyze text content and generate categorized insights using AI.
    
    This function uses the AI service to analyze reflection text and extract insights
    based on four specific categories:
    1. Understanding Myself (self-awareness, emotional shifts, values alignment)
    2. Navigating Relationships (interpersonal growth, politics, leadership influence)
    3. Optimizing Performance (energy patterns, strengths, effectiveness)
    4. Making Progress (goals, accountability, wins, forward motion)
    
    Args:
        text: The extracted text content to analyze
        
    Returns:
        DocumentAnalysis: AI-generated analysis with categorized insights
        
    Raises:
        Exception: If AI processing fails
    """
    try:
        logger.info(f"Starting AI analysis for text content (length: {len(text)})")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Build the analysis prompt
        prompt = _build_insight_analysis_prompt(text)
        
        # Call AI service to generate JSON response
        analysis_result = await _call_ai_for_insights(ai_service, prompt)
        
        # Create DocumentAnalysis object from AI response
        document_analysis = DocumentAnalysis(
            summary=analysis_result.get("summary", ""),
            key_themes=analysis_result.get("key_themes", []),
            sentiment=analysis_result.get("sentiment", "neutral"),
            sentiment_score=analysis_result.get("sentiment_score", 0.0),
            entities=analysis_result.get("entities", {})
        )
        
        logger.info("✅ Successfully generated AI insights")
        return document_analysis
        
    except Exception as e:
        logger.error(f"❌ Error in AI insight analysis: {e}")
        raise Exception(f"AI insight generation failed: {str(e)}")

def _build_insight_analysis_prompt(text: str) -> str:
    """
    Build the AI prompt for insight analysis based on the 4 specified categories.
    
    Args:
        text: The text content to analyze
        
    Returns:
        str: Formatted prompt for AI analysis
    """
    
    return f"""
You are an expert coach and reflection analyst. Analyze the following text and generate insights based on ONLY the four specific categories below. Only generate insights for categories where you find highly relevant content.

TEXT TO ANALYZE:
{text}

ANALYSIS CATEGORIES (only generate insights for categories with highly relevant content):

1. **Understanding Myself**: Self-awareness, emotional shifts, values alignment, personal identity, inner growth
2. **Navigating Relationships**: Interpersonal growth, workplace politics, leadership influence, communication patterns, social dynamics
3. **Optimizing Performance**: Energy patterns, strengths utilization, effectiveness strategies, productivity, skill development
4. **Making Progress**: Goals achievement, accountability systems, wins and celebrations, forward motion, milestone tracking

INSTRUCTIONS:
- Only generate insights for categories where the text contains substantial, relevant content
- Each insight should be specific, actionable, and evidence-based
- Focus on patterns, growth opportunities, and actionable observations
- Provide a concise summary of the overall document
- Identify key themes that emerge from the text
- Assess overall sentiment and provide a numerical score (-1.0 to 1.0)
- Extract named entities (people, places, organizations, concepts)

Generate a JSON response with this exact structure:

{{
    "summary": "2-3 sentence summary of the document's main content and purpose",
    "key_themes": ["theme1", "theme2", "theme3"],
    "sentiment": "positive/negative/neutral",
    "sentiment_score": 0.0,
    "entities": {{
        "people": ["person1", "person2"],
        "places": ["place1", "place2"],
        "organizations": ["org1", "org2"],
        "concepts": ["concept1", "concept2"]
    }},
    "categorized_insights": {{
        "Understanding Myself": [
            {{
                "insight": "Specific insight about self-awareness or values",
                "evidence": "Supporting evidence from the text",
                "confidence": 0.85
            }}
        ],
        "Navigating Relationships": [
            {{
                "insight": "Specific insight about relationships or communication",
                "evidence": "Supporting evidence from the text",
                "confidence": 0.90
            }}
        ],
        "Optimizing Performance": [
            {{
                "insight": "Specific insight about performance or effectiveness",
                "evidence": "Supporting evidence from the text",
                "confidence": 0.75
            }}
        ],
        "Making Progress": [
            {{
                "insight": "Specific insight about goals or progress",
                "evidence": "Supporting evidence from the text",
                "confidence": 0.80
            }}
        ]
    }}
}}

CRITICAL: Only include categories in "categorized_insights" where you find highly relevant content. Empty categories should be omitted entirely from the response.

Return only valid JSON matching the exact structure above.
"""

async def _call_ai_for_insights(ai_service: AIService, prompt: str) -> Dict[str, Any]:
    """
    Call the AI service to generate insights from the prompt.
    
    Args:
        ai_service: Initialized AI service instance
        prompt: The analysis prompt
        
    Returns:
        Dict containing the AI analysis results
        
    Raises:
        Exception: If AI call fails
    """
    try:
        # Use the existing AI service method for JSON responses
        if hasattr(ai_service, '_call_anthropic') and ai_service.anthropic_client:
            response = await ai_service._call_anthropic(prompt)
        elif hasattr(ai_service, '_call_openai') and ai_service.openai_client:
            response = await ai_service._call_openai(prompt)
        else:
            raise Exception("No AI provider available")
            
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        raise Exception("AI returned invalid JSON response")
    except Exception as e:
        logger.error(f"AI service call failed: {e}")
        raise Exception(f"AI processing error: {str(e)}")

def _map_categories_to_enum(categorized_insights: Dict[str, List[Dict]]) -> List[CategoryType]:
    """
    Map the 4 insight categories to CategoryType enum values.
    
    Args:
        categorized_insights: Dictionary of insights by category
        
    Returns:
        List of CategoryType enum values
    """
    categories = []
    
    for category_name, insights in categorized_insights.items():
        if insights:  # Only include categories that have insights
            if category_name in INSIGHT_CATEGORIES:
                # Add the first mapped category type for each insight category
                categories.extend(INSIGHT_CATEGORIES[category_name][:1])
    
    return list(set(categories))  # Remove duplicates