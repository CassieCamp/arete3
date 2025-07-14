from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.roles import router as roles_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.relationships import router as relationships_router
from app.api.v1.endpoints.coaching_relationships import router as coaching_relationships_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.goals import router as goals_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.session_insights import router as session_insights_router
from app.api.v1.endpoints.entries import router as entries_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.discovery_form import router as discovery_form_router
from app.api.v1.endpoints.quotes import router as quotes_router
from app.api.v1.endpoints.destinations import router as destinations_router
from app.api.v1.endpoints.coach import router as coach_router
from app.api.v1.endpoints.freemium import router as freemium_router
from app.api.v1.webhooks.clerk import router as clerk_router
from app.api.v1.deps import org_required, org_optional
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Arete MVP API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection events
@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    await connect_to_mongo()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Close MongoDB connection on shutdown"""
    await close_mongo_connection()
    logger.info("Application shutdown complete")

# Include routers
app.include_router(users_router, prefix="/api/v1/users", tags=["users"])
app.include_router(roles_router, prefix="/api/v1/users", tags=["roles"])
app.include_router(profiles_router, prefix="/api/v1/profiles", tags=["profiles"])
app.include_router(relationships_router, prefix="/api/v1/relationships", tags=["relationships"])
app.include_router(coaching_relationships_router, prefix="/api/v1/coaching-relationships", tags=["coaching-relationships"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(goals_router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(session_insights_router, prefix="/api/v1/session-insights", tags=["session-insights"])
app.include_router(entries_router, prefix="/api/v1/entries", tags=["entries"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(discovery_form_router, prefix="/api/v1/discovery-form", tags=["discovery-form"])
app.include_router(quotes_router, prefix="/api/v1", tags=["quotes"])
app.include_router(destinations_router, prefix="/api/v1/destinations", tags=["destinations"])
app.include_router(coach_router, prefix="/api/v1/coach", tags=["coach"])
app.include_router(freemium_router, prefix="/api/v1/freemium", tags=["freemium"])
app.include_router(clerk_router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Arete MVP API is running"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Arete MVP API", "version": "1.0.0"}


# Test endpoints for organization decorators
@app.get("/api/v1/test/org-required")
async def test_org_required(user_info: dict = Depends(org_required)):
    """Test endpoint for @org_required decorator"""
    return {
        "message": "Access granted to organization-required endpoint",
        "user_id": user_info.get("clerk_user_id"),
        "primary_role": user_info.get("primary_role"),
        "org_id": user_info.get("org_id"),
        "org_role": user_info.get("org_role")
    }


@app.get("/api/v1/test/org-optional")
async def test_org_optional(user_info: dict = Depends(org_optional)):
    """Test endpoint for @org_optional decorator"""
    return {
        "message": "Access granted to organization-optional endpoint",
        "user_id": user_info.get("clerk_user_id"),
        "primary_role": user_info.get("primary_role"),
        "org_id": user_info.get("org_id"),
        "org_role": user_info.get("org_role"),
        "has_org_context": user_info.get("org_id") is not None
    }