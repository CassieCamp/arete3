from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.relationships import router as relationships_router
from app.api.v1.endpoints.coaching_relationships import router as coaching_relationships_router
from app.api.v1.endpoints.documents import router as documents_router
from app.api.v1.endpoints.goals import router as goals_router
from app.api.v1.endpoints.analysis import router as analysis_router
from app.api.v1.endpoints.session_insights import router as session_insights_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.waitlist import router as waitlist_router
from app.api.v1.webhooks.clerk import router as clerk_router
from app.db.mongodb import connect_to_mongo, close_mongo_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Arete MVP API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
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
app.include_router(profiles_router, prefix="/api/v1/profiles", tags=["profiles"])
app.include_router(relationships_router, prefix="/api/v1/relationships", tags=["relationships"])
app.include_router(coaching_relationships_router, prefix="/api/v1/coaching-relationships", tags=["coaching-relationships"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
app.include_router(goals_router, prefix="/api/v1/goals", tags=["goals"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(session_insights_router, prefix="/api/v1/session-insights", tags=["session-insights"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(waitlist_router, prefix="/api/v1/waitlist", tags=["waitlist"])
app.include_router(clerk_router, prefix="/api/v1/webhooks", tags=["webhooks"])


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "Arete MVP API is running"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to Arete MVP API", "version": "1.0.0"}