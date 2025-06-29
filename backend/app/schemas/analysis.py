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
    # Additional fields for frontend display
    strengths: List[str] = []
    development_opportunities: List[str] = []
    # Map backend fields to frontend expected names
    key_themes: List[str] = []  # Will be populated from personality insights
    development_areas: List[str] = []  # Alias for development_opportunities
    summary: str = ""  # Alias for executive_summary
    document_count: int = 0
    goal_count: int = 0
    generated_at: str = ""  # Alias for created_at