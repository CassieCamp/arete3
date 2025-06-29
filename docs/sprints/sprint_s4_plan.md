# Sprint S4: Core Coaching Loop - MVP Technical Plan

## Sprint Goal

**"Enable coaches and clients to create session records with transcripts and generate structured AI summaries that extract key insights, intentions, wins, and people discussed from each session."**

## Overview

Sprint S4 creates the core coaching loop: coaches can add session records with transcripts, the system generates structured summaries from the transcript content, and both parties can view session history with summaries. Focus is on transcript-to-summary workflow.

## Key Features

1. **Session Records**: Simple session creation with date, title, and transcript
2. **AI-Generated Summaries**: Structured summaries extracted from transcript content
3. **Session History**: View all sessions with summaries for a coaching relationship
4. **Read-Only Access**: Both coach and client can view all session data

## 1. Database Models

### CoachingSession Model
```python
class CoachingSession(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    relationship_id: str  # Reference to CoachingRelationship
    session_date: datetime  # When the session occurred
    title: Optional[str] = None  # Optional session title
    transcript: Optional[str] = None  # Raw transcript text
    summary: Optional[SessionSummary] = None  # AI-generated structured summary
    created_by: str  # Who created this session record
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### SessionSummary Model
```python
class SessionSummary(BaseModel):
    session_date: datetime  # Date of the session
    intentions: List[str] = []  # Intentions mentioned in the session
    win_to_celebrate: Optional[str] = None  # Win or achievement to celebrate
    insights_and_challenges: List[dict] = []  # Format: [{"insight": "text", "learning": "text"}]
    people_discussed: List[dict] = []  # Format: [{"name": "text", "context": "text", "optimization_note": "text"}]
    generated_at: datetime = Field(default_factory=datetime.utcnow)
```

## 2. API Endpoints

### Session Management

#### POST /api/v1/sessions/
Create a new session record and optionally generate summary.

**Request:**
```json
{
  "relationship_id": "rel_123",
  "session_date": "2025-01-15T14:00:00Z",
  "title": "Leadership Development Session #3",
  "transcript": "Coach: How did the team meeting go this week?\nClient: It went much better than expected. I practiced the active listening techniques we discussed...",
  "generate_summary": true
}
```

**Response:**
```json
{
  "id": "session_456",
  "relationship_id": "rel_123",
  "session_date": "2025-01-15T14:00:00Z",
  "title": "Leadership Development Session #3",
  "has_transcript": true,
  "has_summary": true,
  "created_by": "user_coach_123",
  "created_at": "2025-01-15T15:30:00Z"
}
```

#### GET /api/v1/sessions/relationship/{relationship_id}
Get all sessions for a relationship with 360 review progress.

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_456",
      "session_date": "2025-01-15T14:00:00Z",
      "title": "Leadership Development Session #3",
      "has_transcript": true,
      "has_summary": true,
      "created_at": "2025-01-15T15:30:00Z"
    }
  ],
  "total_sessions": 1,
  "progress": {
    "session_count": 1,
    "sessions_needed": 3,
    "can_start_360_review": false,
    "progress_percentage": 33.3
  }
}
```

#### GET /api/v1/sessions/{session_id}
Get session details with transcript and summary.

**Response:**
```json
{
  "id": "session_456",
  "session_date": "2025-01-15T14:00:00Z",
  "title": "Leadership Development Session #3",
  "transcript": "Full transcript text...",
  "summary": {
    "session_date": "2025-01-15T14:00:00Z",
    "intentions": [
      "Practice active listening in team meetings",
      "Schedule one-on-ones with direct reports"
    ],
    "win_to_celebrate": "Successfully led the quarterly planning meeting with confidence",
    "insights_and_challenges": [
      {
        "insight": "Realized that team members respond better when I ask questions instead of giving direct instructions",
        "learning": "Questions create engagement and ownership rather than compliance"
      }
    ],
    "people_discussed": [
      {
        "name": "Sarah (Direct Report)",
        "context": "Struggling with project deadlines",
        "optimization_note": "Consider weekly check-ins and breaking large tasks into smaller milestones"
      }
    ],
    "generated_at": "2025-01-15T15:35:00Z"
  }
}
```

#### POST /api/v1/sessions/{session_id}/generate-summary
Generate or regenerate AI summary for a session.

## 3. Service Layer

### SessionService
```python
class SessionService:
    def __init__(self, session_repository, relationship_repository, ai_service):
        self.session_repository = session_repository
        self.relationship_repository = relationship_repository
        self.ai_service = ai_service
    
    async def create_session(self, session_data: dict, created_by: str):
        # Validate user has access to relationship
        # Create session record
        # Optionally generate summary if transcript provided
        # Return created session
        
    async def generate_session_summary(self, session_id: str, user_id: str):
        # Validate user access
        # Get session transcript
        # Generate structured summary using AI
        # Update session with summary
        # Return updated session
```

### AIService
```python
class AIService:
    def __init__(self):
        # Initialize AI client (OpenAI, etc.)
        pass
    
    async def generate_session_summary(self, transcript: str, session_date: datetime) -> SessionSummary:
        """
        Generate structured summary from transcript using AI.
        
        Extracts:
        - Intentions mentioned in the session
        - Win to celebrate
        - Insights and challenges with learnings
        - People discussed with optimization notes
        
        Important: Only extract information explicitly mentioned in the transcript.
        Do not infer or create information not present in the source material.
        """
        
        prompt = f"""
        Analyze this coaching session transcript and extract the following information in JSON format.
        Only include information explicitly mentioned in the transcript. Do not infer or create content.
        
        Session Date: {session_date.isoformat()}
        
        Extract:
        1. intentions: List of specific intentions, commitments, or actions the client mentioned they will take
        2. win_to_celebrate: Any achievement, success, or positive outcome mentioned (or null if none)
        3. insights_and_challenges: Array of objects with "insight" and "learning" for each realization or challenge discussed
        4. people_discussed: Array of objects with "name", "context", and "optimization_note" for people mentioned in relation to work/relationships
        
        Transcript:
        {transcript}
        
        Return only valid JSON matching this structure:
        {{
          "intentions": ["string"],
          "win_to_celebrate": "string or null",
          "insights_and_challenges": [{{"insight": "string", "learning": "string"}}],
          "people_discussed": [{{"name": "string", "context": "string", "optimization_note": "string"}}]
        }}
        """
        
        # Call AI API and parse response
        # Return SessionSummary object
```

## 4. Frontend Components

### SessionList Component
```typescript
interface SessionListProps {
  relationshipId: string;
  userRole: 'coach' | 'client';
}

// List of sessions with:
// - Date and title
// - Summary preview (intentions, win)
// - "Add Session" button for coaches
// - Click to view full session
```

### SessionForm Component
```typescript
interface SessionFormProps {
  relationshipId: string;
  onSessionCreated: (session: Session) => void;
}

// Form with:
// - Date picker
// - Title input (optional)
// - Large textarea for transcript
// - "Generate Summary" checkbox
// - Submit button
```

### SessionView Component
```typescript
interface SessionViewProps {
  sessionId: string;
  userRole: 'coach' | 'client';
}

// Session display with tabs:
// - Summary tab (structured summary)
// - Transcript tab (full transcript)
// - "Regenerate Summary" button for coaches
```

### SessionSummary Component
```typescript
interface SessionSummaryProps {
  summary: SessionSummary;
  sessionCount: number; // Total sessions for this relationship
}

// Structured display:
// - 360 Review Progress Banner (if sessionCount < 3)
// - Date
// - Intentions (bulleted list)
// - Win to celebrate (highlighted)
// - Insights & challenges (expandable cards)
// - People discussed (cards with context)
```

### ProgressBanner Component
```typescript
interface ProgressBannerProps {
  sessionCount: number;
  totalNeeded: number; // Default 3
}

// Progress banner that shows:
// - "X of 3 sessions completed"
// - Progress bar visual
// - "Complete 3 sessions to unlock 360° Review Process"
// - Appears on session views when sessionCount < 3
// - Celebrates when reaching 3 sessions: "🎉 360° Review Process Now Available!"
// - Note: 360 process is stubbed out for future implementation
```

## 5. Database Schema

### coaching_sessions
```json
{
  "_id": "ObjectId",
  "relationship_id": "string",
  "session_date": "datetime",
  "title": "string",
  "transcript": "string",
  "summary": {
    "session_date": "datetime",
    "intentions": ["string"],
    "win_to_celebrate": "string",
    "insights_and_challenges": [
      {
        "insight": "string",
        "learning": "string"
      }
    ],
    "people_discussed": [
      {
        "name": "string",
        "context": "string",
        "optimization_note": "string"
      }
    ],
    "generated_at": "datetime"
  },
  "created_by": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 6. Implementation Plan

### Week 1: Backend Foundation
- [ ] Create CoachingSession model with SessionSummary
- [ ] Create SessionRepository
- [ ] Implement session creation API
- [ ] Add session listing API

### Week 2: AI Integration
- [ ] Implement AIService for summary generation
- [ ] Add summary generation to SessionService
- [ ] Create summary generation API endpoint
- [ ] Test AI summary extraction with sample transcripts

### Week 3: Frontend Components
- [ ] Build SessionList component
- [ ] Build SessionForm component
- [ ] Build SessionView component with tabs
- [ ] Build SessionSummary component
- [ ] Build ProgressBanner component for 360 review unlock

### Week 4: Integration & Polish
- [ ] Connect frontend to backend APIs
- [ ] Add error handling for AI failures
- [ ] Implement summary regeneration
- [ ] Test end-to-end workflow

### Week 5: Testing & Deployment
- [ ] Test with real coaching transcripts
- [ ] Optimize AI prompts for accuracy
- [ ] Handle edge cases and errors
- [ ] Deploy and document

## 7. Success Criteria

### MVP Requirements
- ✅ Coaches can create session records with transcripts
- ✅ AI generates structured summaries from transcripts
- ✅ Both parties can view sessions and summaries
- ✅ Summaries only contain information from transcripts
- ✅ All data is properly secured to relationship participants
- ✅ Progress banner shows 360 review unlock status after 3 sessions

### AI Quality Requirements
- ✅ Summaries accurately reflect transcript content
- ✅ No hallucinated or inferred information
- ✅ Proper extraction of intentions, wins, insights, and people
- ✅ Graceful handling when transcript lacks certain elements

## 8. AI Prompt Strategy

The AI summary generation will use a structured prompt that:
- Explicitly instructs to only extract information present in the transcript
- Provides clear JSON schema for consistent output
- Handles cases where certain elements (like wins) may not be present
- Focuses on coaching-relevant insights and relationship dynamics

## 9. 360 Review Progress Feature

### Progress Tracking Logic
```python
async def get_relationship_progress(self, relationship_id: str) -> dict:
    """Get progress toward 360 review unlock"""
    session_count = await self.session_repository.count_sessions_by_relationship(relationship_id)
    
    return {
        "session_count": session_count,
        "sessions_needed": 3,
        "can_start_360_review": session_count >= 3,
        "progress_percentage": min(100, (session_count / 3) * 100)
    }
```

### Banner Display Rules
- Show progress banner on session list and session detail views
- Display when session_count < 3: "Complete X more sessions to unlock 360° Review"
- Display when session_count >= 3: "🎉 360° Review Process Now Available!"
- Include visual progress indicator (progress bar or step indicator)
- Banner should be prominent but not intrusive to session content
- **Note**: 360° Review Process is stubbed out - clicking will show "Coming Soon" message

### Repository Enhancement
Add session counting method to SessionRepository:

```python
async def count_sessions_by_relationship(self, relationship_id: str) -> int:
    """Count total sessions for a relationship"""
    return await self.collection.count_documents({"relationship_id": relationship_id})
```

## 10. Future Enhancements

- Summary editing and refinement
- Summary templates for different coaching styles
- Trend analysis across multiple sessions
- Export functionality for summaries
- Integration with calendar systems
- **360° Review Process implementation (Sprint S5+)**

This MVP plan focuses on the core transcript-to-summary workflow while maintaining simplicity and ensuring AI-generated content remains grounded in the actual session content. The 360 review progress feature creates anticipation and engagement for future functionality without requiring implementation of the actual 360 review process.