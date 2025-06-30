"""
Dashboard API endpoints

Provides dashboard analytics and data aggregation endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.api.v1.deps import get_current_user
from app.services.dashboard_analytics_service import DashboardAnalyticsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/analytics")
async def get_dashboard_analytics(
    days_back: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard analytics for the current user.
    
    Returns role-specific analytics including:
    - Overview metrics
    - Recent activity
    - Progress summaries
    - Relationship health (for coaches)
    - Coaching journey (for clients)
    """
    try:
        logger.info(f"=== Dashboard analytics requested ===")
        logger.info(f"User: {current_user.get('clerk_user_id')}, Role: {current_user.get('role')}")
        
        analytics_service = DashboardAnalyticsService()
        
        analytics = await analytics_service.get_user_dashboard_analytics(
            user_id=current_user["clerk_user_id"],
            user_role=current_user["role"],
            days_back=days_back
        )
        
        logger.info(f"✅ Dashboard analytics retrieved successfully")
        return {
            "success": True,
            "data": analytics,
            "user_role": current_user["role"],
            "days_back": days_back
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting dashboard analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve dashboard analytics: {str(e)}"
        )


@router.get("/quick-actions")
async def get_quick_actions(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get role-specific quick actions for the dashboard.
    
    Returns a list of quick actions based on user role and current state.
    """
    try:
        logger.info(f"=== Quick actions requested ===")
        logger.info(f"User: {current_user.get('clerk_user_id')}, Role: {current_user.get('role')}")
        
        user_role = current_user["role"]
        
        if user_role == "coach":
            quick_actions = [
                {
                    "id": "manage-clients",
                    "title": "Manage Clients",
                    "description": "View and manage your coaching relationships",
                    "href": "/dashboard/connections",
                    "icon": "Users",
                    "priority": 1
                },
                {
                    "id": "client-insights",
                    "title": "Client Insights",
                    "description": "Review AI-powered client insights",
                    "href": "/dashboard/insights",
                    "icon": "Brain",
                    "priority": 2
                },
                {
                    "id": "invite-client",
                    "title": "Invite Client",
                    "description": "Send invitation to new client",
                    "href": "/dashboard/connections?action=invite",
                    "icon": "UserPlus",
                    "priority": 3
                }
            ]
        else:  # client
            quick_actions = [
                {
                    "id": "view-goals",
                    "title": "My Goals",
                    "description": "Track your personal development goals",
                    "href": "/dashboard/goals",
                    "icon": "Target",
                    "priority": 1
                },
                {
                    "id": "upload-documents",
                    "title": "Upload Documents",
                    "description": "Add documents for analysis",
                    "href": "/dashboard/documents/upload",
                    "icon": "Upload",
                    "priority": 2
                },
                {
                    "id": "view-insights",
                    "title": "My Insights",
                    "description": "Explore your session insights",
                    "href": "/dashboard/insights",
                    "icon": "Brain",
                    "priority": 3
                },
                {
                    "id": "message-coach",
                    "title": "Message Coach",
                    "description": "Connect with your coach",
                    "href": "/dashboard/connections",
                    "icon": "MessageSquare",
                    "priority": 4
                }
            ]
        
        logger.info(f"✅ Quick actions retrieved successfully")
        return {
            "success": True,
            "data": quick_actions,
            "user_role": user_role
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting quick actions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quick actions: {str(e)}"
        )


@router.get("/progress-overview")
async def get_progress_overview(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get progress overview data for the dashboard widget.
    
    Returns role-specific progress metrics and summaries.
    """
    try:
        logger.info(f"=== Progress overview requested ===")
        logger.info(f"User: {current_user.get('clerk_user_id')}, Role: {current_user.get('role')}")
        
        analytics_service = DashboardAnalyticsService()
        
        # Get full analytics data
        analytics = await analytics_service.get_user_dashboard_analytics(
            user_id=current_user["clerk_user_id"],
            user_role=current_user["role"],
            days_back=30
        )
        
        # Extract progress-specific data
        overview = analytics.get("overview", {})
        
        if current_user["role"] == "coach":
            progress_data = {
                "goals": {
                    "total": overview.get("total_client_goals", 0),
                    "completed": overview.get("completed_client_goals", 0),
                    "active": overview.get("active_client_goals", 0),
                    "completionRate": round((overview.get("completed_client_goals", 0) / max(overview.get("total_client_goals", 1), 1)) * 100, 1)
                },
                "insights": {
                    "total": overview.get("total_session_insights", 0),
                    "thisMonth": overview.get("recent_session_insights", 0),
                    "trend": "up" if overview.get("recent_session_insights", 0) > 0 else "stable",
                    "trendValue": 15
                },
                "relationships": {
                    "total": overview.get("active_clients", 0),
                    "active": overview.get("active_clients", 0),
                    "healthScore": analytics.get("relationship_health", {}).get("health_score", 85)
                },
                "sessions": {
                    "thisMonth": overview.get("recent_session_insights", 0),
                    "lastMonth": max(0, overview.get("recent_session_insights", 0) - 2),
                    "trend": "up"
                },
                "overallProgress": min(100, (overview.get("active_clients", 0) * 20) + (overview.get("recent_session_insights", 0) * 5)),
                "streakDays": 12
            }
        else:  # client
            progress_data = {
                "goals": {
                    "total": overview.get("active_goals", 0) + overview.get("completed_goals", 0),
                    "completed": overview.get("completed_goals", 0),
                    "active": overview.get("active_goals", 0),
                    "completionRate": round((overview.get("completed_goals", 0) / max(overview.get("active_goals", 0) + overview.get("completed_goals", 0), 1)) * 100, 1)
                },
                "insights": {
                    "total": overview.get("total_session_insights", 0),
                    "thisMonth": overview.get("recent_session_insights", 0),
                    "trend": "up" if overview.get("recent_session_insights", 0) > 0 else "stable",
                    "trendValue": 12
                },
                "relationships": {
                    "total": overview.get("active_coaching_relationships", 0),
                    "active": overview.get("active_coaching_relationships", 0),
                    "healthScore": 95
                },
                "sessions": {
                    "thisMonth": overview.get("recent_session_insights", 0),
                    "lastMonth": max(0, overview.get("recent_session_insights", 0) - 1),
                    "trend": "up"
                },
                "overallProgress": min(100, (overview.get("completed_goals", 0) * 25) + (overview.get("recent_session_insights", 0) * 10)),
                "streakDays": analytics.get("coaching_journey", {}).get("journey_length_days", 0) % 30
            }
        
        logger.info(f"✅ Progress overview retrieved successfully")
        return {
            "success": True,
            "data": progress_data,
            "user_role": current_user["role"]
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting progress overview: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve progress overview: {str(e)}"
        )