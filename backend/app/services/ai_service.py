import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import anthropic
from app.core.config import settings
from app.models.client_baseline import ClientBaseline, PersonalityInsight, CommunicationStyle, GoalPattern, InitialChallenge, BaselineMetadata
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key) if settings.anthropic_api_key else None
        
    async def generate_client_baseline(
        self, 
        user_id: str,
        clerk_user_id: str,
        documents_text: List[Dict[str, Any]],  # [{"filename": str, "content": str, "category": str}]
        generated_by: str
    ) -> ClientBaseline:
        """
        Generate a comprehensive client baseline from document analysis.
        """
        start_time = time.time()
        
        try:
            logger.info(f"=== AIService.generate_client_baseline called ===")
            logger.info(f"user_id: {user_id}, documents: {len(documents_text)}")
            
            # Prepare analysis context
            total_text_length = sum(len(doc["content"]) for doc in documents_text)
            document_summaries = []
            
            for doc in documents_text:
                doc_summary = f"Document: {doc['filename']} (Category: {doc['category']})\n"
                doc_summary += f"Content: {doc['content'][:2000]}{'...' if len(doc['content']) > 2000 else ''}\n"
                document_summaries.append(doc_summary)
            
            combined_content = "\n\n---\n\n".join(document_summaries)
            
            # Truncate if too long
            if len(combined_content) > settings.baseline_max_text_length:
                combined_content = combined_content[:settings.baseline_max_text_length] + "\n\n[Content truncated due to length...]"
            
            # Generate baseline using AI
            baseline_data = await self._call_ai_for_baseline(combined_content, len(documents_text), total_text_length)
            
            processing_time = time.time() - start_time
            
            # Create baseline object
            baseline = ClientBaseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                executive_summary=baseline_data["executive_summary"],
                personality_insights=[PersonalityInsight(**insight) for insight in baseline_data["personality_insights"]],
                communication_style=CommunicationStyle(**baseline_data["communication_style"]) if baseline_data.get("communication_style") else None,
                goal_patterns=[GoalPattern(**pattern) for pattern in baseline_data["goal_patterns"]],
                initial_challenges=[InitialChallenge(**challenge) for challenge in baseline_data["initial_challenges"]],
                strengths=baseline_data.get("strengths", []),
                development_opportunities=baseline_data.get("development_opportunities", []),
                source_document_ids=[doc.get("document_id", "") for doc in documents_text],
                analysis_scope=f"Analysis of {len(documents_text)} documents covering {', '.join(set(doc['category'] for doc in documents_text))}",
                status="completed",
                metadata=BaselineMetadata(
                    ai_provider=settings.ai_provider,
                    model_version=settings.ai_model,
                    processing_time_seconds=processing_time,
                    document_count=len(documents_text),
                    total_text_length=total_text_length,
                    generation_prompt_version=settings.baseline_prompt_version
                ),
                generated_by=generated_by,
                completed_at=datetime.utcnow()
            )
            
            logger.info(f"✅ Successfully generated baseline for user {user_id}")
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Error generating baseline: {e}")
            processing_time = time.time() - start_time
            
            # Return failed baseline
            return ClientBaseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                executive_summary="Baseline generation failed",
                analysis_scope=f"Failed analysis of {len(documents_text)} documents",
                status="failed",
                processing_error=str(e),
                metadata=BaselineMetadata(
                    ai_provider=settings.ai_provider,
                    model_version=settings.ai_model,
                    processing_time_seconds=processing_time,
                    document_count=len(documents_text),
                    total_text_length=total_text_length,
                    generation_prompt_version=settings.baseline_prompt_version
                ),
                generated_by=generated_by
            )
    
    async def _call_ai_for_baseline(self, content: str, doc_count: int, total_length: int) -> Dict[str, Any]:
        """Call AI provider to generate baseline data"""
        prompt = self._build_baseline_prompt(content, doc_count, total_length)
        
        try:
            if settings.ai_provider == "openai" and self.openai_client:
                return await self._call_openai(prompt)
            elif settings.ai_provider == "anthropic" and self.anthropic_client:
                return await self._call_anthropic(prompt)
            else:
                # Fallback logic
                if self.openai_client:
                    logger.info("Falling back to OpenAI")
                    return await self._call_openai(prompt)
                elif self.anthropic_client:
                    logger.info("Falling back to Anthropic")
                    return await self._call_anthropic(prompt)
                else:
                    raise Exception("No AI provider available")
        except Exception as e:
            logger.error(f"Error calling AI provider: {e}")
            raise
    
    async def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.ai_model,
                messages=[
                    {"role": "system", "content": "You are an expert coaching analyst. Generate comprehensive client baselines based on document analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.ai_max_tokens,
                temperature=settings.ai_temperature,
                timeout=settings.ai_timeout_seconds
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic API"""
        try:
            response = await self.anthropic_client.messages.create(
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
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def _build_baseline_prompt(self, content: str, doc_count: int, total_length: int) -> str:
        """Build the comprehensive baseline generation prompt"""
        
        return f"""
Analyze the following client documents and generate a comprehensive coaching baseline. Focus on extracting insights that will be valuable for both the client and their coach.

DOCUMENT ANALYSIS SCOPE:
- Number of documents: {doc_count}
- Total content length: {total_length} characters
- Analysis goal: Create foundational client understanding

DOCUMENTS TO ANALYZE:
{content}

ANALYSIS REQUIREMENTS:
1. Only extract information explicitly present in the documents
2. Do not infer or create information not supported by evidence
3. Provide specific quotes or examples as evidence for each insight
4. Focus on coaching-relevant observations
5. Maintain a positive, development-focused tone

Generate a JSON response with the following structure:

{{
  "executive_summary": "2-3 sentence high-level overview of the client based on document analysis",
  "personality_insights": [
    {{
      "trait": "Specific personality trait or characteristic",
      "description": "Detailed description of how this trait manifests",
      "evidence": ["Direct quote or example from documents", "Another supporting example"],
      "confidence_score": 0.85
    }}
  ],
  "communication_style": {{
    "primary_style": "Primary communication approach (e.g., Direct, Collaborative, Analytical)",
    "characteristics": ["Specific communication traits observed"],
    "preferences": ["Preferred communication methods/styles mentioned"],
    "examples": ["Evidence from documents showing communication style"]
  }},
  "goal_patterns": [
    {{
      "pattern_type": "Type of goal-setting pattern (e.g., Achievement-Oriented, Relationship-Focused)",
      "description": "How this pattern manifests in their goal-setting",
      "examples": ["Specific examples from documents"],
      "suggested_approach": "Coaching approach recommendation for this pattern"
    }}
  ],
  "initial_challenges": [
    {{
      "challenge_area": "Specific area needing development",
      "description": "Description of the challenge based on document evidence",
      "impact_level": "Low/Medium/High",
      "suggested_focus": "Coaching recommendation for addressing this challenge",
      "supporting_evidence": ["Quotes or examples supporting this challenge identification"]
    }}
  ],
  "strengths": ["List of identified strengths with document support"],
  "development_opportunities": ["Areas for growth mentioned or implied in documents"]
}}

IMPORTANT GUIDELINES:
- Confidence scores should reflect how strongly the evidence supports each insight (0.0-1.0)
- Include 3-5 personality insights maximum
- Focus on actionable insights for coaching
- Maintain client confidentiality and professional tone
- If insufficient information exists for any section, provide fewer items rather than speculating

Return only valid JSON matching the exact structure above.
"""