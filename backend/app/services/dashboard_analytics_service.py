"""
Dashboard Analytics Service

This service aggregates data from various sources to provide dashboard analytics.
It fetches and processes data for dashboard widgets like QuickActions and ProgressOverview.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from app.services.goal_service import GoalService
from app.services.session_insight_service import SessionInsightService
from app.services.coaching_relationship_service import CoachingRelationshipService
from app.repositories.document_repository import DocumentRepository
from app.repositories.coaching_relationship_repository import CoachingRelationshipRepository
from app.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)


class DashboardAnalyticsService:
    def __init__(self):
        self.goal_service = GoalService()
        self.session_insight_service = SessionInsightService()
        self.document_repository = DocumentRepository()
        
        # Initialize repositories needed for CoachingRelationshipService
        self.coaching_relationship_repository = CoachingRelationshipRepository()
        self.user_repository = UserRepository()
        
        # Initialize CoachingRelationshipService with required dependencies
        self.coaching_relationship_service = CoachingRelationshipService(
            self.coaching_relationship_repository,
            self.user_repository
        )
    async def get_analytics(
        self,
        user_id: str,
        user_role: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics data specifically for the dashboard /analytics endpoint.
        This method aggregates data for the current user including:
        - Total number of goals and completed goals
        - Count of recent session insights  
        - Summary of upcoming sessions or deadlines
        """
        try:
            logger.info(f"=== DashboardAnalyticsService.get_analytics called ===")
            logger.info(f"user_id: {user_id}, role: {user_role}, days_back: {days_back}")
            
            since_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Get comprehensive analytics first
            full_analytics = await self.get_user_dashboard_analytics(user_id, user_role, days_back)
            
            # Extract and structure the specific data needed for the analytics endpoint
            overview = full_analytics.get("overview", {})
            
            if user_role == 'coach':
                analytics_data = {
                    "goals": {
                        "total": overview.get("total_client_goals", 0),
                        "completed": overview.get("completed_client_goals", 0),
                        "active": overview.get("active_client_goals", 0)
                    },
                    "session_insights": {
                        "total": overview.get("total_session_insights", 0),
                        "recent": overview.get("recent_session_insights", 0)
                    },
                    "clients": {
                        "active": overview.get("active_clients", 0)
                    },
                    "upcoming_sessions": await self._get_upcoming_sessions(user_id, user_role),
                    "recent_activity": full_analytics.get("recent_activity", [])
                }
            else:  # client
                analytics_data = {
                    "goals": {
                        "total": overview.get("active_goals", 0) + overview.get("completed_goals", 0),
                        "completed": overview.get("completed_goals", 0),
                        "active": overview.get("active_goals", 0)
                    },
                    "session_insights": {
                        "total": overview.get("total_session_insights", 0),
                        "recent": overview.get("recent_session_insights", 0)
                    },
                    "coaching_relationships": {
                        "active": overview.get("active_coaching_relationships", 0)
                    },
                    "upcoming_sessions": await self._get_upcoming_sessions(user_id, user_role),
                    "recent_activity": full_analytics.get("recent_activity", [])
                }
            
            logger.info(f"✅ Analytics data prepared successfully")
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}


    async def get_user_dashboard_analytics(
        self,
        user_id: str,
        user_role: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics for a user"""
        try:
            logger.info(f"=== DashboardAnalyticsService.get_user_dashboard_analytics called ===")
            logger.info(f"user_id: {user_id}, role: {user_role}")
            
            since_date = datetime.utcnow() - timedelta(days=days_back)
            
            if user_role == 'coach':
                return await self._get_coach_analytics(user_id, since_date)
            else:
                return await self._get_client_analytics(user_id, since_date)
                
        except Exception as e:
            logger.error(f"❌ Error getting dashboard analytics: {e}")
            return {}

    async def _get_coach_analytics(self, coach_user_id: str, since_date: datetime) -> Dict[str, Any]:
        """Get analytics specific to coaches"""
        try:
            # Get coaching relationships
            relationships_data = await self.coaching_relationship_service.get_user_relationships(coach_user_id)
            active_relationships = relationships_data.get("active", [])
            client_ids = [rel.client_user_id for rel in active_relationships]
            
            # Session insights analytics
            total_insights = 0
            recent_insights = 0
            all_insights = []
            
            for client_id in client_ids:
                try:
                    # Get insights for each client
                    client_insights = await self.session_insight_service.insight_repository.get_insights_by_user(client_id)
                    all_insights.extend(client_insights)
                    total_insights += len(client_insights)
                    recent_insights += len([i for i in client_insights if i.created_at >= since_date])
                except Exception as e:
                    logger.warning(f"Error getting insights for client {client_id}: {e}")
                    continue
            
            # Goal progress analytics
            total_goals = 0
            active_goals = 0
            completed_goals = 0
            
            for client_id in client_ids:
                try:
                    client_goals = await self.goal_service.get_all_user_goals(client_id)
                    total_goals += len(client_goals)
                    active_goals += len([g for g in client_goals if g.status == 'active'])
                    completed_goals += len([g for g in client_goals if g.status == 'completed'])
                except Exception as e:
                    logger.warning(f"Error getting goals for client {client_id}: {e}")
                    continue
            
            # Document analytics
            total_documents = 0
            for client_id in client_ids:
                try:
                    client_docs = await self.document_repository.get_documents_by_user_id(client_id)
                    total_documents += len(client_docs)
                except Exception as e:
                    logger.warning(f"Error getting documents for client {client_id}: {e}")
                    continue
            
            return {
                "overview": {
                    "active_clients": len(active_relationships),
                    "total_session_insights": total_insights,
                    "recent_session_insights": recent_insights,
                    "total_client_goals": total_goals,
                    "active_client_goals": active_goals,
                    "completed_client_goals": completed_goals,
                    "total_client_documents": total_documents
                },
                "recent_activity": await self._get_recent_activity(coach_user_id, since_date, "coach", all_insights),
                "client_progress": await self._get_client_progress_summary(client_ids),
                "relationship_health": await self._get_relationship_health(active_relationships)
            }
            
        except Exception as e:
            logger.error(f"Error getting coach analytics: {e}")
            return {}

    async def _get_client_analytics(self, client_user_id: str, since_date: datetime) -> Dict[str, Any]:
        """Get analytics specific to clients"""
        try:
            # Get coaching relationships
            relationships_data = await self.coaching_relationship_service.get_user_relationships(client_user_id)
            active_relationships = relationships_data.get("active", [])
            
            # Session insights
            insights = await self.session_insight_service.insight_repository.get_insights_by_user(client_user_id)
            recent_insights = [i for i in insights if i.created_at >= since_date]
            
            # Goals
            goals = await self.goal_service.get_all_user_goals(client_user_id)
            active_goals = [g for g in goals if g.status == 'active']
            completed_goals = [g for g in goals if g.status == 'completed']
            
            # Documents
            documents = await self.document_repository.get_documents_by_user_id(client_user_id)
            processed_docs = [d for d in documents if d.is_processed]
            
            return {
                "overview": {
                    "active_coaching_relationships": len(active_relationships),
                    "total_session_insights": len(insights),
                    "recent_session_insights": len(recent_insights),
                    "active_goals": len(active_goals),
                    "completed_goals": len(completed_goals),
                    "uploaded_documents": len(documents),
                    "processed_documents": len(processed_docs)
                },
                "recent_activity": await self._get_recent_activity(client_user_id, since_date, "client", insights),
                "goal_progress": await self._get_goal_progress_summary(goals),
                "coaching_journey": await self._get_coaching_journey_summary(client_user_id, insights, goals)
            }
            
        except Exception as e:
            logger.error(f"Error getting client analytics: {e}")
            return {}

    async def _get_recent_activity(
        self, 
        user_id: str, 
        since_date: datetime, 
        user_role: str,
        insights: List = None
    ) -> List[Dict[str, Any]]:
        """Get recent activity for dashboard"""
        activities = []
        
        try:
            # Use provided insights or fetch them
            if insights is None:
                if user_role == "client":
                    insights = await self.session_insight_service.insight_repository.get_insights_by_user(user_id)
                else:
                    # For coaches, get insights from all their clients
                    relationships_data = await self.coaching_relationship_service.get_user_relationships(user_id)
                    active_relationships = relationships_data.get("active", [])
                    insights = []
                    for rel in active_relationships:
                        try:
                            client_insights = await self.session_insight_service.insight_repository.get_insights_by_user(rel.client_user_id)
                            insights.extend(client_insights)
                        except Exception as e:
                            logger.warning(f"Error getting insights for client {rel.client_user_id}: {e}")
                            continue
            
            # Recent session insights
            recent_insights = [i for i in insights if i.created_at >= since_date]
            for insight in recent_insights[-5:]:  # Last 5
                activities.append({
                    "type": "session_insight",
                    "title": "Session insight generated",
                    "description": insight.session_title or "Untitled session",
                    "timestamp": insight.created_at,
                    "url": f"/dashboard/insights/{insight.id}"
                })
            
            # Recent goals (for clients)
            if user_role == "client":
                try:
                    goals = await self.goal_service.get_all_user_goals(user_id)
                    recent_goals = [g for g in goals if g.created_at >= since_date]
                    for goal in recent_goals[-3:]:  # Last 3
                        activities.append({
                            "type": "goal",
                            "title": "New goal created",
                            "description": goal.goal_statement or goal.title,
                            "timestamp": goal.created_at,
                            "url": "/dashboard/goals"
                        })
                except Exception as e:
                    logger.warning(f"Error getting recent goals: {e}")
            
            # Sort by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []

    async def _get_client_progress_summary(self, client_ids: List[str]) -> List[Dict[str, Any]]:
        """Get progress summary for coach's clients"""
        progress_data = []
        
        for client_id in client_ids:
            try:
                # Get client goals
                goals = await self.goal_service.get_all_user_goals(client_id)
                active_goals = [g for g in goals if g.status == 'active']
                completed_goals = [g for g in goals if g.status == 'completed']
                
                # Get recent insights
                insights = await self.session_insight_service.insight_repository.get_insights_by_user(client_id)
                recent_insights = [i for i in insights if i.created_at >= datetime.utcnow() - timedelta(days=30)]
                
                # Calculate progress score (simple algorithm)
                progress_score = min(100, (len(completed_goals) * 20) + (len(recent_insights) * 10))
                
                progress_data.append({
                    "client_id": client_id,
                    "active_goals": len(active_goals),
                    "completed_goals": len(completed_goals),
                    "recent_insights": len(recent_insights),
                    "progress_score": progress_score
                })
                
            except Exception as e:
                logger.error(f"Error getting progress for client {client_id}: {e}")
                continue
        
        return progress_data

    async def _get_relationship_health(self, relationships: List) -> Dict[str, Any]:
        """Calculate relationship health metrics"""
        if not relationships:
            return {"overall_health": "No relationships", "health_score": 0}
        
        total_score = 0
        for relationship in relationships:
            # Simple health calculation based on activity
            days_since_created = (datetime.utcnow() - relationship.created_at).days
            if days_since_created < 7:
                score = 100  # New relationship
            elif days_since_created < 30:
                score = 80   # Active relationship
            else:
                score = 60   # Established relationship
            
            total_score += score
        
        avg_score = total_score / len(relationships)
        
        if avg_score >= 80:
            health_status = "Excellent"
        elif avg_score >= 60:
            health_status = "Good"
        else:
            health_status = "Needs Attention"
        
        return {
            "overall_health": health_status,
            "health_score": avg_score,
            "total_relationships": len(relationships)
        }

    async def _get_goal_progress_summary(self, goals: List) -> Dict[str, Any]:
        """Get goal progress summary for clients"""
        if not goals:
            return {"total_goals": 0, "completion_rate": 0, "active_goals": 0}
        
        active_goals = [g for g in goals if g.status == 'active']
        completed_goals = [g for g in goals if g.status == 'completed']
        
        completion_rate = (len(completed_goals) / len(goals)) * 100 if goals else 0
        
        return {
            "total_goals": len(goals),
            "active_goals": len(active_goals),
            "completed_goals": len(completed_goals),
            "completion_rate": round(completion_rate, 1)
        }

    async def _get_coaching_journey_summary(
        self, 
        client_id: str, 
        insights: List, 
        goals: List
    ) -> Dict[str, Any]:
        """Get coaching journey summary for clients"""
        journey_start = None
        if insights:
            journey_start = min(insight.created_at for insight in insights)
        elif goals:
            journey_start = min(goal.created_at for goal in goals)
        
        if not journey_start:
            return {"journey_length_days": 0, "milestones": []}
        
        journey_days = (datetime.utcnow() - journey_start).days
        
        # Calculate milestones
        milestones = []
        if len(insights) >= 1:
            milestones.append("First session insight generated")
        if len(goals) >= 1:
            milestones.append("First goal created")
        if len([g for g in goals if g.status == 'completed']) >= 1:
            milestones.append("First goal completed")
        if len(insights) >= 5:
            milestones.append("5+ session insights generated")
        
        return {
            "journey_length_days": journey_days,
            "milestones": milestones,
            "total_insights": len(insights),
            "total_goals": len(goals)
        }
    async def _get_upcoming_sessions(self, user_id: str, user_role: str) -> List[Dict[str, Any]]:
        """Get upcoming sessions or deadlines for the user"""
        try:
            # For now, return mock data since we don't have a sessions/calendar system yet
            # This can be expanded when session scheduling is implemented
            upcoming = []
            
            if user_role == 'coach':
                # Mock upcoming sessions for coaches
                upcoming = [
                    {
                        "type": "coaching_session",
                        "title": "Coaching Session",
                        "description": "Scheduled session with client",
                        "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                        "time": "2:00 PM"
                    },
                    {
                        "type": "goal_review",
                        "title": "Goal Review",
                        "description": "Monthly client goal review",
                        "date": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                        "time": "10:00 AM"
                    }
                ]
            else:  # client
                # Mock upcoming sessions for clients
                upcoming = [
                    {
                        "type": "coaching_session",
                        "title": "Coaching Session",
                        "description": "Session with your coach",
                        "date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
                        "time": "2:00 PM"
                    },
                    {
                        "type": "goal_deadline",
                        "title": "Goal Check-in",
                        "description": "Review progress on current goals",
                        "date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                        "time": "Self-paced"
                    }
                ]
            
            logger.info(f"Generated {len(upcoming)} upcoming sessions for {user_role}")
            return upcoming
            
        except Exception as e:
            logger.error(f"Error getting upcoming sessions: {e}")
            return []
