from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import Field
from app.models.journey.base import UserOwnedDocument
from app.models.journey.enums import CategoryType, ReviewStatus

class Insight(UserOwnedDocument):
    """Complete insight model for MongoDB persistence"""
    title: str = Field(..., description="Title of the insight")
    content: str = Field(..., description="Main insight content")
    summary: Optional[str] = Field(default=None, description="Brief summary")
    category: CategoryType = Field(..., description="Primary category")
    subcategories: List[CategoryType] = Field(default_factory=list, description="Additional categories")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    source_id: str = Field(..., description="ID of the reflection source")
    source_title: Optional[str] = Field(default=None, description="Title of source for reference")
    source_excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from source")
    review_status: ReviewStatus = Field(default=ReviewStatus.DRAFT)
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="AI confidence")
    is_favorite: bool = Field(default=False, description="User marked as favorite")
    is_archived: bool = Field(default=False, description="User archived this insight")
    user_rating: Optional[int] = Field(default=None, ge=1, le=5, description="User rating 1-5")
    view_count: int = Field(default=0, description="Number of times viewed")
    last_viewed_at: Optional[datetime] = Field(default=None)
    is_actionable: bool = Field(default=False, description="Contains actionable items")
    suggested_actions: List[str] = Field(default_factory=list, description="AI-suggested actions")
    ai_model_version: Optional[str] = Field(default=None, description="AI model used for generation")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="AI processing metadata")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When insight was generated")
    archived_at: Optional[datetime] = Field(default=None)

    class Config:
        collection_name = "journey_insights"