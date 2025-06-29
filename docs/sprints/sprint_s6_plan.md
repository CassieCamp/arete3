# Sprint S6: AI Analysis & Baseline Generation - Technical Plan

## Sprint Goal

**"Enable AI-powered analysis of user-uploaded documents to generate comprehensive Client Baselines that provide coaches and clients with foundational insights into personality, communication style, and initial goals."**

## Overview

Sprint S6 introduces AI-powered document analysis to create "Client Baselines" - comprehensive summaries that capture a client's personality traits, communication patterns, goal-setting tendencies, and initial challenges. This baseline serves as a foundational reference point for both coaches and clients, enhancing the coaching relationship with data-driven insights.

## Architecture Overview

The system follows the established Arete architecture patterns:

- **Frontend Layer**: Document Library with Generate Baseline button → Baseline Generation UI → Baseline Display Component
- **API Layer**: POST /api/v1/analysis/generate-baseline, GET /api/v1/analysis/baseline/:user_id, PUT /api/v1/analysis/baseline/:baseline_id  
- **Service Layer**: AnalysisService orchestrates AIService and DocumentService
- **Data Layer**: ClientBaseline Model with BaselineRepository, integrates with existing Document and User collections
- **External Services**: OpenAI API (primary) with Anthropic API fallback

## 1. AI Service Integration

### Environment Configuration

Update [`backend/app/core/config.py`](backend/app/core/config.py:16):

```python
class Settings(BaseSettings):
    # ... existing fields ...
    
    # AI Service Configuration
    openai_api_key: Optional[str] = None  # Already exists
    anthropic_api_key: Optional[str] = None  # New fallback option
    ai_provider: str = "openai"  # Primary provider
    ai_model: str = "gpt-4"  # Default model
    ai_max_tokens: int = 4000  # Response limit
    ai_temperature: float = 0.3  # Consistency over creativity
    ai_timeout_seconds: int = 120  # Request timeout
    
    # Baseline Generation Settings
    baseline_max_documents: int = 10  # Limit documents per baseline
    baseline_max_text_length: int = 50000  # Character limit for analysis
    baseline_prompt_version: str = "v1.0"  # For tracking prompt iterations
```

### Requirements Update

Add to [`backend/requirements.txt`](backend/requirements.txt):

```txt
# AI Services
anthropic  # Fallback AI provider
```

## 2. Database Models

### ClientBaseline Model

Create new file: [`backend/app/models/client_baseline.py`](backend/app/models/client_baseline.py)

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
        raise ValueError("Invalid ObjectId")

class BaselineStatus(str, Enum):
    """Status of baseline generation"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PersonalityInsight(BaseModel):
    """Individual personality trait or characteristic"""
    trait: str  # e.g., "Communication Style", "Decision Making"
    description: str  # Detailed description of the trait
    evidence: List[str]  # Quotes or examples from documents
    confidence_score: float = Field(ge=0.0, le=1.0)  # AI confidence in this insight

class GoalPattern(BaseModel):
    """Identified goal-setting patterns and preferences"""
    pattern_type: str  # e.g., "Achievement-Oriented", "Relationship-Focused"
    description: str
    examples: List[str]  # Specific examples from documents
    suggested_approach: str  # Coaching approach recommendation

class CommunicationStyle(BaseModel):
    """Communication preferences and patterns"""
    primary_style: str  # e.g., "Direct", "Collaborative", "Analytical"
    characteristics: List[str]  # Specific communication traits
    preferences: List[str]  # Preferred communication methods/styles
    examples: List[str]  # Evidence from documents

class InitialChallenge(BaseModel):
    """Identified challenges or areas for development"""
    challenge_area: str  # e.g., "Time Management", "Team Leadership"
    description: str
    impact_level: str  # "Low", "Medium", "High"
    suggested_focus: str  # Coaching recommendation
    supporting_evidence: List[str]

class BaselineMetadata(BaseModel):
    """Metadata about the baseline generation process"""
    ai_provider: str  # "openai" or "anthropic"
    model_version: str  # e.g., "gpt-4", "claude-3"
    processing_time_seconds: float
    document_count: int
    total_text_length: int
    generation_prompt_version: str  # For tracking prompt iterations

class ClientBaseline(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str  # Foreign key to User (client)
    clerk_user_id: str  # Clerk user ID for direct integration
    
    # Core baseline content
    executive_summary: str  # High-level overview of the client
    personality_insights: List[PersonalityInsight] = Field(default_factory=list)
    communication_style: Optional[CommunicationStyle] = None
    goal_patterns: List[GoalPattern] = Field(default_factory=list)
    initial_challenges: List[InitialChallenge] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)  # Identified strengths
    development_opportunities: List[str] = Field(default_factory=list)
    
    # Source information
    source_document_ids: List[str] = Field(default_factory=list)  # Documents analyzed
    analysis_scope: str  # Description of what was analyzed
    
    # Processing metadata
    status: BaselineStatus = BaselineStatus.PENDING
    processing_error: Optional[str] = None
    metadata: Optional[BaselineMetadata] = None
    
    # Access control
    generated_by: str  # User ID of who triggered generation
    visible_to_client: bool = True  # Always true based on requirements
    visible_to_coach: bool = True   # Always true based on requirements
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    def __str__(self) -> str:
        return f"ClientBaseline(user_id='{self.user_id}', status='{self.status}', created_at='{self.created_at}')"
```

## 3. Service Layer

### AIService Implementation

Create new file: [`backend/app/services/ai_service.py`](backend/app/services/ai_service.py)

```python
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
```

### AnalysisService Implementation

Create new file: [`backend/app/services/analysis_service.py`](backend/app/services/analysis_service.py)

```python
from typing import List, Optional
from app.models.client_baseline import ClientBaseline
from app.repositories.baseline_repository import BaselineRepository
from app.repositories.document_repository import DocumentRepository
from app.services.ai_service import AIService
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    def __init__(self, baseline_repository: BaselineRepository, document_repository: DocumentRepository):
        self.baseline_repository = baseline_repository
        self.document_repository = document_repository
        self.ai_service = AIService()
    
    async def generate_client_baseline(
        self, 
        user_id: str, 
        clerk_user_id: str,
        generated_by: str,
        document_ids: Optional[List[str]] = None
    ) -> ClientBaseline:
        """
        Generate a client baseline from their uploaded documents.
        """
        try:
            logger.info(f"=== AnalysisService.generate_client_baseline called ===")
            logger.info(f"user_id: {user_id}, generated_by: {generated_by}")
            
            # Get user's documents
            if document_ids:
                documents = []
                for doc_id in document_ids:
                    doc = await self.document_repository.get_document_by_id(doc_id)
                    if doc and doc.user_id == user_id:  # Security check
                        documents.append(doc)
            else:
                documents = await self.document_repository.get_documents_by_user_id(user_id)
            
            if not documents:
                raise ValueError("No documents found for analysis")
            
            # Filter to processed documents with extracted text
            processed_docs = [doc for doc in documents if doc.is_processed and doc.extracted_text]
            
            if not processed_docs:
                raise ValueError("No processed documents with extracted text found")
            
            # Limit number of documents
            if len(processed_docs) > settings.baseline_max_documents:
                processed_docs = sorted(processed_docs, key=lambda x: x.created_at, reverse=True)
                processed_docs = processed_docs[:settings.baseline_max_documents]
                logger.info(f"Limited analysis to {settings.baseline_max_documents} most recent documents")
            
            # Prepare document content for AI analysis
            documents_text = []
            for doc in processed_docs:
                documents_text.append({
                    "document_id": str(doc.id),
                    "filename": doc.file_name,
                    "content": doc.extracted_text,
                    "category": doc.category.value if hasattr(doc.category, 'value') else str(doc.category)
                })
            
            # Create pending baseline record
            pending_baseline = ClientBaseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                executive_summary="Baseline generation in progress...",
                status="processing",
                source_document_ids=[str(doc.id) for doc in processed_docs],
                analysis_scope=f"Processing {len(processed_docs)} documents",
                generated_by=generated_by
            )
            
            # Save pending baseline
            saved_baseline = await self.baseline_repository.create_baseline(pending_baseline)
            logger.info(f"Created pending baseline with ID: {saved_baseline.id}")
            
            # Generate baseline using AI
            completed_baseline = await self.ai_service.generate_client_baseline(
                user_id=user_id,
                clerk_user_id=clerk_user_id,
                documents_text=documents_text,
                generated_by=generated_by
            )
            
            # Update the baseline with results
            completed_baseline.id = saved_baseline.id
            updated_baseline = await self.baseline_repository.update_baseline(
                str(saved_baseline.id),
                completed_baseline.model_dump(exclude={"id"})
            )
            
            logger.info(f"✅ Successfully generated baseline for user {user_id}")
            return updated_baseline
            
        except Exception as e:
            logger.error(f"❌ Error in generate_client_baseline: {e}")
            raise
```

## 4. Repository Layer

### BaselineRepository Implementation

Create new file: [`backend/app/repositories/baseline_repository.py`](backend/app/repositories/baseline_repository.py)

```python
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.mongodb import get_database
from app.models.client_baseline import ClientBaseline
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BaselineRepository:
    def __init__(self):
        self.db = get_database()
        self.collection: AsyncIOMotorCollection = self.db.client_baselines
    
    async def create_baseline(self, baseline: ClientBaseline) -> ClientBaseline:
        """Create a new client baseline"""
        try:
            logger.info(f"=== BaselineRepository.create_baseline called ===")
            logger.info(f"Creating baseline for user_id: {baseline.user_id}")
            
            baseline_dict = baseline.model_dump(by_alias=True, exclude={"id"})
            result = await self.collection.insert_one(baseline_dict)
            
            baseline.id = result.inserted_id
            logger.info(f"✅ Created baseline with ID: {result.inserted_id}")
            return baseline
            
        except Exception as e:
            logger.error(f"❌ Error creating baseline: {e}")
            raise
    
    async def get_baseline_by_user_id(self, user_id: str) -> Optional[ClientBaseline]:
        """Get the most recent baseline for a user"""
        try:
            logger.info(f"=== BaselineRepository.get_baseline_by_user_id called ===")
            logger.info(f"user_id: {user_id}")
            
            cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1).limit(1)
            result = await cursor.to_list(length=1)
            
            if result:
                baseline = ClientBaseline(**result[0])
                logger.info(f"✅ Found baseline for user: {user_id}")
                return baseline
            else:
                logger.info(f"No baseline found for user: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting baseline by user ID: {e}")
            return None
    
    async def update_baseline(self, baseline_id: str, update_data: Dict[str, Any]) -> Optional[ClientBaseline]:
        """Update a baseline"""
        try:
            logger.info(f"=== BaselineRepository.update_baseline called ===")
            logger.info(f"baseline_id: {baseline_id}")
            
            if not ObjectId.is_valid(baseline_id):
                logger.error(f"Invalid ObjectId: {baseline_id}")
                return None
            
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(baseline_id)},
                {"$set": update_data},
                return_document=True
            )
            
            if result:
                logger.info(f"✅ Updated baseline: {baseline_id}")
                return ClientBaseline(**result)
            else:
                logger.error(f"Baseline not found for update: {baseline_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error updating baseline: {e}")
            return None
```

## 5. API Endpoints

### Analysis Endpoints

Create new file: [`backend/app/api/v1/endpoints/analysis.py`](backend/app/api/v1/endpoints/analysis.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.v1.deps import get_current_user_clerk_id
from app.services.analysis_service import AnalysisService
from app.services.user_service import UserService
from app.repositories.baseline_repository import BaselineRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.analysis import BaselineGenerationRequest, BaselineResponse
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/generate-baseline", response_model=BaselineResponse)
async def generate_client_baseline(
    request: BaselineGenerationRequest,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Generate a client baseline from uploaded documents."""
    try:
        logger.info(f"=== Generate baseline endpoint called ===")
        logger.info(f"clerk_user_id: {clerk_user_id}, target_user_id: {request.user_id}")
        
        # Get requesting user
        user_service = UserService()
        requesting_user = await user_service.get_user_by_clerk_id(clerk_user_id)
        if not requesting_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requesting user not found"
            )
        
        # Get target user
        target_user = await user_service.get_user_by_id(request.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        # Initialize services
        baseline_repository = BaselineRepository()
        document_repository = DocumentRepository()
        analysis_service = AnalysisService(baseline_repository, document_repository)
        
        # Generate baseline
        baseline = await analysis_service.generate_client_baseline(
            user_id=request.user_id,
            clerk_user_id=target_user.clerk_user_id,
            generated_by=str(requesting_user.id),
            document_ids=request.document_ids
        )
        
        logger.info(f"✅ Generated baseline with ID: {baseline.id}")
        
        return BaselineResponse(
            id=str(baseline.id),
            user_id=baseline.user_id,
            executive_summary=baseline.executive_summary,
            status=baseline.status,
            created_at=baseline.created_at.isoformat(),
            completed_at=baseline.completed_at.isoformat() if baseline.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate baseline: {str(e)}"
        )

@router.get("/baseline/{user_id}", response_model=BaselineResponse)
async def get_client_baseline(
    user_id: str,
    clerk_user_id: str = Depends(get_current_user_clerk_id)
):
    """Get the most recent client baseline for a user."""
    try:
        baseline_repository = BaselineRepository()
        baseline = await baseline_repository.get_baseline_by_user_id(user_id)
        
        if not baseline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Baseline not found"
            )
        
        return BaselineResponse(
            id=str(baseline.id),
            user_id=baseline.user_id,
            executive_summary=baseline.executive_summary,
            status=baseline.status,
            created_at=baseline.created_at.isoformat(),
            completed_at=baseline.completed_at.isoformat() if baseline.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve baseline: {str(e)}"
        )
```

### API Schemas

Create new file: [`backend/app/schemas/analysis.py`](backend/app/schemas/analysis.py)

```python
from pydantic import BaseModel
from typing import List, Optional

class BaselineGenerationRequest(BaseModel):
    user_id: str  # User ID whose baseline to generate
    document_ids: Optional[List[str]] = None  # Optional specific documents to analyze

class BaselineResponse(BaseModel):
    id: str
    user_id: str
    executive_summary: str
    status: str
    created_at: str
    completed_at: Optional[str]
```

## 6. Frontend Integration

### Baseline Generation Component

Create new file: [`frontend/src/components/baseline/BaselineGenerator.tsx`](frontend/src/components/baseline/BaselineGenerator.tsx)

```typescript
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/context/AuthContext";

interface Document {
  id: string;
  file_name: string;
  category: string;
  is_processed: boolean;
}

interface BaselineGeneratorProps {
  userId: string;
  documents: Document[];
  onBaselineGenerated: (baselineId: string) => void;
  userRole: 'coach' | 'client';
}

export default function BaselineGenerator({ 
  userId, 
  documents, 
  onBaselineGenerated, 
  userRole 
}: BaselineGeneratorProps) {
  const { getAuthToken } = useAuth();
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const processedDocuments = documents.filter(doc => doc.is_processed);

  const handleGenerateBaseline = async () => {
    try {
      setIsGenerating(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      const requestBody = {
        user_id: userId
      };

      const response = await fetch('http://localhost:8000/api/v1/analysis/generate-baseline', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to generate baseline with status ${response.status}`);
      }

      const baseline = await response.json();
      onBaselineGenerated(baseline.id);

    } catch (error) {
      console.error('Error generating baseline:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate baseline');
    } finally {
      setIsGenerating(false);
    }
  };

  if (processedDocuments.length === 0) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Documents Available
          </h3>
          <p className="text-gray-600">
            Upload and process documents before generating a baseline analysis.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generate Client Baseline</CardTitle>
        <CardDescription>
          Create an AI-powered analysis of personality, communication style, and goals based on uploaded documents.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 text-red-800 border border-red-200 rounded-md">
            <p className="font-medium">Generation Failed</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Generation Info */}
        <div className="p-4 bg-blue-50 text-blue-800 border border-blue-200 rounded-md">
          <p className="text-sm">
            <strong>What will be analyzed:</strong> The AI will examine document content to identify
            personality traits, communication patterns, goal-setting preferences, strengths, and development opportunities.
          </p>
          <p className="text-sm mt-2">
            <strong>Processing time:</strong> This typically takes 30-60 seconds depending on document length.
          </p>
        </div>

        {/* Generate Button */}
        <Button
          onClick={handleGenerateBaseline}
          disabled={isGenerating}
          className="w-full bg-blue-600 hover:bg-blue-700"
          size="lg"
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Generating Baseline...
            </>
          ) : (
            <>
              🧠 Generate AI Baseline
            </>
          )}
        </Button>

        {/* Role-specific messaging */}
        <div className="text-xs text-gray-500 text-center">
          {userRole === 'coach' ? (
            "As a coach, you can generate baselines for your clients to better understand their profile."
          ) : (
            "Generate your personal baseline to gain insights into your communication style and goals."
          )}
        </div>
      </CardContent>
    </Card>
  );
}
```

### Baseline Display Component

Create new file: [`frontend/src/components/baseline/BaselineDisplay.tsx`](frontend/src/components/baseline/BaselineDisplay.tsx)

```typescript
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";

interface ClientBaseline {
  id: string;
  user_id: string;
  executive_summary: string;
  status: string;
  created_at: string;
  completed_at?: string;
}

interface BaselineDisplayProps {
  userId: string;
  onRegenerateRequest: () => void;
  userRole: 'coach' | 'client';
}

export default function BaselineDisplay({ userId, onRegenerateRequest, userRole }: BaselineDisplayProps) {
  const { getAuthToken } = useAuth();
  const [baseline, setBaseline] = useState<ClientBaseline | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchBaseline();
  }, [userId]);

  const fetchBaseline = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const token = await getAuthToken();
      if (!token) {
        throw new Error('Authentication token not available');
      }

      const response = await fetch(`http://localhost:8000/api/v1/analysis/baseline/${userId}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setBaseline(null);
          return;
        }
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch baseline with status ${response.status}`);
      }

      const baselineData = await response.json();
      setBaseline(baselineData);

    } catch (error) {
      console.error('Error fetching baseline:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch baseline');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading baseline...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-6xl mb-4">⚠️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Baseline</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={fetchBaseline} variant="outline">
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!baseline) {
    return (
      <Card>
        <CardContent className="text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Baseline Generated</h3>
          <p className="text-gray-600 mb-4">
            Generate an AI baseline to get insights into personality, communication style, and goals.
          </p>
          <Button onClick={onRegenerateRequest} className="bg-blue-600 hover:bg-blue-700">
            Generate Baseline
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div>
            <CardTitle>Client Baseline Analysis</CardTitle>
            <CardDescription>
              AI-generated insights from document analysis
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              baseline.status === 'completed'
                ? 'bg-green-100 text-green-800'
                : baseline.status === 'processing'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {baseline.status}
            </span>
            <Button
              onClick={onRegenerateRequest}
              variant="outline"
              size="sm"
            >
              Regenerate
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Executive Summary */}
        <div>
          <h4 className="text-sm font-medium text-gray-900 mb-2">Executive Summary</h4>
          <p className="text-sm text-gray-700 leading-relaxed">
            {baseline.executive_summary}
          </p>
        </div>

        {/* Metadata */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Generated: {new Date(baseline.created_at).toLocaleDateString()}</span>
            {baseline.completed_at && (
              <span>Completed: {new Date(baseline.completed_at).toLocaleDateString()}</span>
            )}
          </div>
        </div>

        {/* Quarterly Review Note */}
        <div className="mt-4 text-center text-xs text-gray-500 p-2 bg-gray-50 rounded-md">
          <p>This baseline is a snapshot of your journey's start. It will be updated quarterly to reflect your growth and progress.</p>
        </div>
      </CardContent>
    </Card>
  );
}
```

### Integration with Document Library

Update [`frontend/src/app/dashboard/documents/page.tsx`](frontend/src/app/dashboard/documents/page.tsx) to include baseline generation:

```typescript
// Add to imports
import BaselineGenerator from "@/components/baseline/BaselineGenerator";
import BaselineDisplay from "@/components/baseline/BaselineDisplay";

// Add state for baseline management
const [showBaselineGenerator, setShowBaselineGenerator] = useState(false);
const [baselineGenerated, setBaselineGenerated] = useState(false);

// Add baseline section after documents grid
{/* Baseline Analysis Section */}
<div className="mt-8">
  <h3 className="text-xl font-semibold text-gray-900 mb-4">
    AI Baseline Analysis
  </h3>
  
  {showBaselineGenerator ? (
    <BaselineGenerator
      userId={user_id}
      documents={documents}
      onBaselineGenerated={(baselineId) => {
        setBaselineGenerated(true);
        setShowBaselineGenerator(false);
      }}
      userRole={user?.role as 'coach' | 'client'}
    />
  ) : (
    <BaselineDisplay
      userId={user_id}
      onRegenerateRequest={() => setShowBaselineGenerator(true)}
      userRole={user?.role as 'coach' | 'client'}
    />
  )}
</div>
```

## 7. Implementation Plan

### Phase 1: Backend Foundation (Week 1)
- [ ] Update [`backend/app/core/config.py`](backend/app/core/config.py) with AI configuration
- [ ] Add `anthropic` to [`backend/requirements.txt`](backend/requirements.txt)
- [ ] Create [`backend/app/models/client_baseline.py`](backend/app/models/client_baseline.py)
- [ ] Create [`backend/app/repositories/baseline_repository.py`](backend/app/repositories/baseline_repository.py)
- [ ] Create [`backend/app/schemas/analysis.py`](backend/app/schemas/analysis.py)

### Phase 2: AI Service Integration (Week 2)
- [ ] Create [`backend/app/services/ai_service.py`](backend/app/services/ai_service.py)
- [ ] Implement AI prompt engineering and testing
- [ ] Create [`backend/app/services/analysis_service.py`](backend/app/services/analysis_service.py)
- [ ] Add error handling and fallback mechanisms

### Phase 3: API Development (Week 3)
- [ ] Create [`backend/app/api/v1/endpoints/analysis.py`](backend/app/api/v1/endpoints/analysis.py)
- [ ] Update main router to include analysis endpoints
- [ ] Add proper authentication and authorization
- [ ] Test API endpoints with sample data

### Phase 4: Frontend Components (Week 4)
- [ ] Create [`frontend/src/components/baseline/BaselineGenerator.tsx`](frontend/src/components/baseline/BaselineGenerator.tsx)
- [ ] Create [`frontend/src/components/baseline/BaselineDisplay.tsx`](frontend/src/components/baseline/BaselineDisplay.tsx)
- [ ] Update document library page to include baseline functionality
- [ ] Add proper error handling and loading states

### Phase 5: Integration & Testing (Week 5)
- [ ] End-to-end testing with real documents
- [ ] AI prompt optimization based on results
- [ ] Performance testing and optimization
- [ ] Security review and access control verification
- [ ] Documentation and deployment preparation

## 8. Security & Scalability Considerations

### Security
- **API Key Management**: Store AI provider keys securely in environment variables
- **Access Control**: Ensure users can only generate/view baselines they have permission for
- **Data Privacy**: Implement proper data handling for sensitive document content
- **Input Validation**: Validate all inputs to prevent injection attacks
- **Rate Limiting**: Implement rate limiting for AI API calls to prevent abuse

### Scalability
- **Async Processing**: Use background tasks for baseline generation to avoid blocking requests
- **Caching**: Cache baseline results to reduce redundant AI API calls
- **Database Indexing**: Add proper indexes on user_id and created_at fields
- **AI Provider Fallback**: Implement fallback between OpenAI and Anthropic for reliability
- **Document Limits**: Enforce limits on document count and size for analysis

### Performance Optimization
- **Text Truncation**: Limit document text length to stay within AI token limits
- **Batch Processing**: Process multiple documents efficiently in single AI calls
- **Response Streaming**: Consider streaming responses for long-running operations
- **Error Recovery**: Implement retry logic with exponential backoff

## 9. Success Criteria

### MVP Requirements
- ✅ Coaches and clients can trigger baseline generation from document library
- ✅ AI analyzes uploaded documents to extract personality insights
- ✅ System generates comprehensive baseline with communication style analysis
- ✅ Goal patterns and initial challenges are identified from document content
- ✅ Baselines are visible to both coaches and clients (shared access)
- ✅ Error handling for failed AI processing
- ✅ Integration follows existing Arete architecture patterns

### Quality Requirements
- ✅ AI analysis only extracts information explicitly present in documents
- ✅ No hallucinated or inferred information beyond document evidence
- ✅ Proper confidence scoring for personality insights
- ✅ Professional, development-focused tone in all generated content
- ✅ Graceful handling of insufficient document content

### Technical Requirements
- ✅ Secure API key management for AI providers
- ✅ Proper error handling and fallback mechanisms
- ✅ Performance optimization for document processing
- ✅ Scalable architecture supporting future enhancements
- ✅ Comprehensive logging for debugging and monitoring

## 10. Future Enhancements

### Sprint S7+ Considerations
- **Baseline Evolution**: Track how baselines change over time with new documents
- **Coach Insights**: Generate coaching-specific recommendations based on baselines
- **Goal Integration**: Automatically suggest goals based on baseline analysis
- **Progress Tracking**: Compare baseline insights with actual progress over time
- **Advanced Analytics**: Aggregate insights across client populations (anonymized)
- **Custom Prompts**: Allow coaches to customize analysis focus areas
- **Multi-language Support**: Extend AI analysis to non-English documents
- **Integration with Sessions**: Connect baseline insights to session summaries

This comprehensive technical plan provides a solid foundation for implementing AI-powered Client Baseline generation in Sprint S6, following established Arete patterns while introducing powerful new capabilities for coaches and clients.