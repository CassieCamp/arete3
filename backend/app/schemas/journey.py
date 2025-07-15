"""
Journey System API Schemas

This module contains Pydantic schemas for Journey System API requests and responses.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.journey.enums import CategoryType, ReviewStatus, ProcessingStatus


# Request Schemas

class ReflectionCreateRequest(BaseModel):
    """Schema for creating a new reflection"""
    title: str = Field(..., description="Title or name of the reflection source")
    description: Optional[str] = Field(default=None, description="Optional description of the source")
    content: Optional[str] = Field(default=None, description="Raw text content of the reflection")
    categories: List[CategoryType] = Field(default_factory=list, description="Categories assigned to this reflection")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    auto_process: bool = Field(default=True, description="Whether to automatically process this source")
    processing_priority: int = Field(default=0, description="Processing priority (higher = more urgent)")


class InsightCreateRequest(BaseModel):
    """Schema for creating a new insight"""
    title: str = Field(..., description="Title of the insight")
    content: str = Field(..., description="Main insight content")
    summary: Optional[str] = Field(default=None, description="Brief summary of the insight")
    category: CategoryType = Field(..., description="Primary category of the insight")
    subcategories: List[CategoryType] = Field(default_factory=list, description="Additional categories")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    source_excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from the source")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence score (0.0-1.0)")
    is_actionable: bool = Field(default=False, description="Whether this insight suggests actions")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested action items")


# Response Schemas

class InsightResponse(BaseModel):
    """Schema for insight responses"""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Title of the insight")
    content: str = Field(..., description="Main insight content")
    summary: Optional[str] = Field(default=None, description="Brief summary of the insight")
    category: CategoryType = Field(..., description="Primary category of the insight")
    subcategories: List[CategoryType] = Field(default_factory=list, description="Additional categories")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    source_id: str = Field(..., description="ID of the reflection source this insight came from")
    source_title: Optional[str] = Field(default=None, description="Title of the source for quick reference")
    source_excerpt: Optional[str] = Field(default=None, description="Relevant excerpt from the source")
    review_status: ReviewStatus = Field(..., description="Current review status")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence score (0.0-1.0)")
    is_favorite: bool = Field(default=False, description="Whether user marked as favorite")
    is_actionable: bool = Field(default=False, description="Whether this insight suggests actions")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested action items")
    user_rating: Optional[int] = Field(default=None, description="User rating (1-5)")
    view_count: int = Field(default=0, description="Number of times viewed")
    created_at: datetime = Field(..., description="When the insight was created")
    updated_at: datetime = Field(..., description="When the insight was last updated")
    generated_at: datetime = Field(..., description="When insight was generated")


class ReflectionResponse(BaseModel):
    """Schema for reflection responses"""
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Title or name of the reflection source")
    description: Optional[str] = Field(default=None, description="Optional description of the source")
    content: Optional[str] = Field(default=None, description="Raw text content of the reflection")
    categories: List[CategoryType] = Field(default_factory=list, description="Categories assigned to this reflection")
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    processing_status: ProcessingStatus = Field(..., description="Current processing status")
    insight_count: int = Field(default=0, description="Number of insights generated from this reflection")
    word_count: Optional[int] = Field(default=None, description="Word count of the content")
    created_at: datetime = Field(..., description="When the reflection was created")
    updated_at: datetime = Field(..., description="When the reflection was last updated")


class ReflectionWithInsightsResponse(BaseModel):
    """Schema for reflection with its insights"""
    reflection: ReflectionResponse = Field(..., description="The reflection data")
    insights: List[InsightResponse] = Field(default_factory=list, description="Associated insights")
    insight_count: int = Field(..., description="Total number of insights")


class JourneyFeedItem(BaseModel):
    """Schema for journey feed items"""
    type: str = Field(..., description="Type of item (reflection or insight)")
    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="Title of the item")
    content: Optional[str] = Field(default=None, description="Content of the item")
    summary: Optional[str] = Field(default=None, description="Summary (for insights)")
    description: Optional[str] = Field(default=None, description="Description (for reflections)")
    categories: Optional[List[CategoryType]] = Field(default=None, description="Categories (for reflections)")
    category: Optional[CategoryType] = Field(default=None, description="Primary category (for insights)")
    tags: List[str] = Field(default_factory=list, description="Tags")
    processing_status: Optional[ProcessingStatus] = Field(default=None, description="Processing status (for reflections)")
    review_status: Optional[ReviewStatus] = Field(default=None, description="Review status (for insights)")
    insight_count: Optional[int] = Field(default=None, description="Insight count (for reflections)")
    source_id: Optional[str] = Field(default=None, description="Source ID (for insights)")
    source_title: Optional[str] = Field(default=None, description="Source title (for insights)")
    is_favorite: Optional[bool] = Field(default=None, description="Favorite status (for insights)")
    is_actionable: Optional[bool] = Field(default=None, description="Actionable status (for insights)")
    suggested_actions: Optional[List[str]] = Field(default=None, description="Suggested actions (for insights)")
    confidence_score: Optional[float] = Field(default=None, description="Confidence score (for insights)")
    user_rating: Optional[int] = Field(default=None, description="User rating (for insights)")
    view_count: Optional[int] = Field(default=None, description="View count (for insights)")
    created_at: datetime = Field(..., description="When the item was created")
    updated_at: datetime = Field(..., description="When the item was last updated")
    generated_at: Optional[datetime] = Field(default=None, description="When generated (for insights)")


class JourneyFeedResponse(BaseModel):
    """Schema for journey feed response"""
    items: List[JourneyFeedItem] = Field(..., description="Feed items")
    total_count: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
    category_counts: Optional[Dict[str, int]] = Field(default=None, description="Count of items per category for filter UI")

