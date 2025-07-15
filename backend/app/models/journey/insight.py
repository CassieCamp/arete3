"""
Journey System Insight Models

This module contains models for insights generated from reflection sources.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from .base import UserOwnedDocument
from .enums import CategoryType, ReviewStatus


class Insight(UserOwnedDocument):
    """Model for insights generated from reflection sources"""
    
    # Core content
    title: str = Field(..., description="Title of the insight")
    content: str = Field(..., description="Main insight content")
    summary: Optional[str] = Field(default=None, description="Brief summary of the insight")
    
    # Categorization and organization
    category: CategoryType = Field(..., description="Primary category of the insight")
    subcategories: List[CategoryType] = Field(default_factory=list, description="Additional categories")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    
    # Source tracking
    source_id: str = Field(..., description="ID of the reflection source this insight came from")
    source_title: Optional[str] = Field(default=None, description="Title of the source for quick reference")
    source_excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from the source")
    
    # Review and quality
    review_status: ReviewStatus = Field(default=ReviewStatus.DRAFT, description="Current review status")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence score (0.0-1.0)")
    quality_score: Optional[float] = Field(default=None, description="Quality assessment score (0.0-1.0)")
    
    # User interaction
    is_favorite: bool = Field(default=False, description="Whether user marked as favorite")
    is_archived: bool = Field(default=False, description="Whether insight is archived")
    user_rating: Optional[int] = Field(default=None, description="User rating (1-5)")
    user_notes: Optional[str] = Field(default=None, description="User's personal notes")
    
    # Actionability
    is_actionable: bool = Field(default=False, description="Whether this insight suggests actions")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested action items")
    related_goals: List[str] = Field(default_factory=list, description="IDs of related goals")
    
    # Relationships and connections
    related_insight_ids: List[str] = Field(default_factory=list, description="IDs of related insights")
    theme_connections: List[str] = Field(default_factory=list, description="Connected themes or patterns")
    
    # Analytics and metadata
    view_count: int = Field(default=0, description="Number of times viewed")
    last_viewed_at: Optional[datetime] = Field(default=None, description="When last viewed")
    word_count: Optional[int] = Field(default=None, description="Word count of the insight content")
    
    # AI processing metadata
    ai_model_version: Optional[str] = Field(default=None, description="AI model version used to generate")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional AI processing data")
    
    # Timestamps for lifecycle tracking
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When insight was generated")
    reviewed_at: Optional[datetime] = Field(default=None, description="When insight was reviewed")
    archived_at: Optional[datetime] = Field(default=None, description="When insight was archived")
    
    def mark_as_favorite(self):
        """Mark insight as favorite"""
        self.is_favorite = True
        self.updated_at = datetime.utcnow()
    
    def remove_from_favorites(self):
        """Remove insight from favorites"""
        self.is_favorite = False
        self.updated_at = datetime.utcnow()
    
    def archive(self):
        """Archive the insight"""
        self.is_archived = True
        self.archived_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def unarchive(self):
        """Unarchive the insight"""
        self.is_archived = False
        self.archived_at = None
        self.updated_at = datetime.utcnow()
    
    def increment_view_count(self):
        """Increment view count and update last viewed timestamp"""
        self.view_count += 1
        self.last_viewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_user_rating(self, rating: int):
        """Set user rating (1-5)"""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self.user_rating = rating
        self.updated_at = datetime.utcnow()
    
    def update_review_status(self, status: ReviewStatus):
        """Update review status"""
        self.review_status = status
        if status == ReviewStatus.REVIEWED:
            self.reviewed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    class Config:
        """Pydantic configuration"""
        json_encoders = {datetime: lambda v: v.isoformat()}