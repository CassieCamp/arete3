# Goal Model Specification - Human-Centered Approach

## Overview
This document specifies the updated Goal model structure that moves away from traditional SMART goals toward a more human-centered approach focusing on meaningful objectives and qualitative progress tracking.

## Current vs. New Structure

### Current Goal Model (Traditional)
```python
class Goal(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    title: str
    description: Optional[str] = None
    status: str = "active"  # active, completed, paused, cancelled
    priority: str = "medium"  # low, medium, high
    target_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    progress_percentage: int = Field(default=0, ge=0, le=100)
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### New Goal Model (Human-Centered)
```python
class Goal(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    
    # Core human-centered fields
    goal_statement: str  # Simple "what you want to work on"
    success_vision: str  # "How you'll know it's working"
    progress_emoji: str = "😐"  # Current emotional state
    progress_notes: Optional[str] = None  # Optional qualitative notes
    
    # Progress history for tracking emotional journey
    progress_history: List[ProgressEntry] = Field(default_factory=list)
    
    # AI and document integration
    ai_suggested: bool = False  # Flag for AI-generated goals
    source_documents: List[str] = Field(default_factory=list)  # Document IDs that inspired this goal
    
    # Simplified metadata
    status: str = "active"  # active, completed, paused
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProgressEntry(BaseModel):
    emoji: str
    notes: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## Key Changes Explained

### 1. Core Structure Transformation
- **`title` → `goal_statement`**: More conversational, focuses on "what you want to work on"
- **`description` → `success_vision`**: Shifts from describing the goal to describing how success feels
- **`progress_percentage` → `progress_emoji`**: Replaces quantitative metrics with emotional indicators

### 2. Removed Fields
- `priority`: Eliminates artificial prioritization pressure
- `target_date`: Removes deadline stress, focuses on continuous improvement
- `completion_date`: Success is ongoing, not a one-time achievement

### 3. New Fields
- `progress_history`: Tracks emotional journey over time
- `ai_suggested`: Identifies AI-generated vs. user-created goals
- `source_documents`: Links goals to inspiring documents

### 4. Simplified Status
- Reduced from 4 states to 3: `active`, `completed`, `paused`
- Removes `cancelled` to maintain positive framing

## Progress Emoji System

### Suggested Emoji Categories
- **Positive Progress**: 😊, 🎉, ✨, 🌟, 💪
- **Neutral/Steady**: 😐, 🤔, 📈, 🔄, ⚖️
- **Challenging**: 😔, 😤, 🤯, 🌧️, 🏔️
- **Breakthrough**: 🚀, 💡, 🎯, 🌈, 🔥

### Usage Guidelines
- Users select emoji that represents their current feeling toward the goal
- No right or wrong choices - purely subjective
- Encourages regular check-ins without pressure
- Creates visual timeline of emotional journey

## AI Integration Points

### Document-Based Goal Discovery
```python
async def suggest_goals_from_documents(user_id: str, document_ids: List[str]) -> List[GoalSuggestion]:
    """
    Analyze uploaded documents to suggest meaningful goals
    Returns goal_statement + success_vision pairs for user selection
    """
```

### Success Vision Guidance
```python
async def enhance_success_vision(goal_statement: str, user_context: dict) -> List[str]:
    """
    Provide success vision suggestions based on goal statement and user context
    Helps users articulate how success feels rather than metrics
    """
```

## Database Migration Strategy

### Phase 1: Add New Fields
- Add new fields with default values
- Maintain backward compatibility
- Existing goals continue to function

### Phase 2: Data Transformation
- Convert `title` → `goal_statement`
- Transform `description` → `success_vision` (with AI assistance if needed)
- Convert `progress_percentage` → appropriate `progress_emoji`

### Phase 3: Remove Old Fields
- Deprecate unused fields after successful migration
- Clean up database schema

## Service Layer Updates

### GoalService Enhancements
```python
class GoalService:
    async def suggest_goals_from_documents(self, user_id: str, document_ids: List[str]) -> List[GoalSuggestion]
    async def create_goal_from_suggestion(self, user_id: str, suggestion: GoalSuggestion) -> Goal
    async def update_progress_emotion(self, goal_id: str, user_id: str, emoji: str, notes: Optional[str] = None) -> Goal
    async def get_progress_timeline(self, goal_id: str, user_id: str) -> List[ProgressEntry]
    async def enhance_success_vision(self, goal_statement: str, user_context: dict) -> List[str]
```

## Frontend Implications

### Goal Creation Flow
1. **Document Analysis**: AI analyzes uploaded documents
2. **Goal Suggestions**: Present curated goal options
3. **Goal Selection**: User chooses from suggestions or creates custom
4. **Success Vision**: Guide user to define how success feels
5. **Initial Progress**: Set starting emotional state

### Progress Tracking Interface
- Large, friendly emoji selector
- Optional text area for progress notes
- Visual timeline of emotional journey
- No pressure metrics or percentages

### Goal Dashboard
- Card-based layout showing goal statement + current emoji
- Success vision prominently displayed
- Progress timeline accessible via expansion
- Gentle, encouraging language throughout

## Benefits of This Approach

### For Users
- **Less Intimidating**: No complex metrics or deadlines
- **More Meaningful**: Focus on personal feelings and experiences
- **Encouraging**: Positive framing without failure states
- **Intuitive**: Emoji-based progress is universally understood

### For Coaches
- **Deeper Insights**: Emotional progress reveals more than percentages
- **Better Conversations**: Success visions provide rich discussion topics
- **Authentic Progress**: Qualitative tracking shows real human development
- **Document Integration**: Goals emerge naturally from client context

### For the Platform
- **AI Enhancement**: Document analysis drives personalized suggestions
- **User Engagement**: Emoji tracking encourages regular interaction
- **Data Richness**: Emotional timelines provide valuable coaching insights
- **Differentiation**: Human-centered approach sets platform apart

## Implementation Priority

1. **Update Goal Model** - Core data structure changes
2. **Migrate Existing Data** - Transform current goals gracefully
3. **Enhance Goal Service** - Add AI-powered suggestion methods
4. **Update API Endpoints** - Support new goal structure
5. **Rebuild Frontend Components** - Human-centered interfaces
6. **Test & Validate** - Ensure smooth user experience

This specification provides the foundation for implementing a more human-centered approach to goal management that prioritizes emotional well-being and meaningful progress over traditional metrics.