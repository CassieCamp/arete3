"""
Dashboard Analytics Response Schemas

Defines the structure of data returned by dashboard analytics endpoints.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class GoalsAnalytics(BaseModel):
    """Goals analytics data"""
    total: int
    completed: int
    active: int


class SessionInsightsAnalytics(BaseModel):
    """Session insights analytics data"""
    total: int
    recent: int


class ClientsAnalytics(BaseModel):
    """Clients analytics data (for coaches)"""
    active: int


class CoachingRelationshipsAnalytics(BaseModel):
    """Coaching relationships analytics data (for clients)"""
    active: int


class UpcomingSession(BaseModel):
    """Upcoming session or deadline"""
    type: str  # "coaching_session", "goal_review", "goal_deadline"
    title: str
    description: str
    date: str  # ISO format datetime string
    time: str


class RecentActivity(BaseModel):
    """Recent activity item"""
    type: str  # "session_insight", "goal", etc.
    title: str
    description: str
    timestamp: datetime
    url: Optional[str] = None


class DashboardAnalyticsResponse(BaseModel):
    """Complete dashboard analytics response"""
    goals: GoalsAnalytics
    session_insights: SessionInsightsAnalytics
    clients: Optional[ClientsAnalytics] = None  # Only for coaches
    coaching_relationships: Optional[CoachingRelationshipsAnalytics] = None  # Only for clients
    upcoming_sessions: List[UpcomingSession]
    recent_activity: List[RecentActivity]


class DashboardAnalyticsAPIResponse(BaseModel):
    """API wrapper for dashboard analytics response"""
    success: bool
    data: DashboardAnalyticsResponse
    user_role: str
    days_back: int