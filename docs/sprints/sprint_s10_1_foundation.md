# Sprint S10.1: Foundation & Database Migration

**Epic**: [Sprint S10 Application Redesign](./sprint_s10_redesign_epic.md)  
**Duration**: 2 weeks  
**Priority**: Critical  
**Dependencies**: None (foundational sprint)

## Sprint Overview

This sprint establishes the foundational changes required for the application redesign. It focuses on database schema changes, collection renames, and backend infrastructure updates that will support all subsequent sprints.

## Sprint Goals

1. **Migrate database schema** to support unified entry system and destinations
2. **Rename core collections** with backward compatibility
3. **Create new collections** for enhanced features
4. **Update backend services** and API endpoints
5. **Establish migration procedures** with rollback capability

## Database Schema Changes

### Collection Renames

#### 1. `session_insights` → `entries`
```javascript
// Migration strategy: Rename collection and add entry_type field
{
  _id: ObjectId,
  
  // NEW: Unified entry fields
  entry_type: String, // "session" | "fresh_thought" (backfill existing as "session")
  title: String, // AI-generated title (backfill from existing data)
  
  // EXISTING: Maintain all current fields for backward compatibility
  coaching_relationship_id: ObjectId?,
  client_user_id: ObjectId,
  coach_user_id: ObjectId?,
  session_date: Date,
  transcript_content: String,
  tags: [String],
  metadata: Object,
  
  // EXISTING: AI Analysis Results (maintain all)
  celebrations: [Object],
  intentions: [Object],
  client_discoveries: [Object],
  goal_progress: [Object],
  coaching_presence: Object?,
  powerful_questions: [Object],
  action_items: [Object],
  emotional_shifts: [Object],
  values_beliefs: [Object],
  communication_patterns: [Object],
  
  // NEW: Goal Detection
  detected_goals: [{
    goal_statement: String,
    confidence: Number, // 0-1
    suggested: Boolean,
    accepted: Boolean?,
    destination_id: ObjectId?
  }],
  
  // EXISTING: Status and timestamps (maintain all)
  status: String,
  processing_error: String?,
  overall_session_quality: String?,
  created_at: Date,
  updated_at: Date,
  completed_at: Date?
}
```

**Migration Steps**:
1. Create new `entries` collection
2. Copy all documents from `session_insights` to `entries`
3. Add `entry_type: "session"` to all migrated documents
4. Generate titles for existing entries using AI
5. Create indexes on new collection
6. Update application to use `entries` collection
7. Keep `session_insights` as backup during transition

#### 2. `goals` → `destinations`
```javascript
// Migration strategy: Rename collection and add Three Big Ideas support
{
  _id: ObjectId,
  user_id: ObjectId,
  
  // RENAMED: Core fields
  destination_statement: String, // Renamed from goal_statement
  success_vision: String, // Maintained
  
  // NEW: Three Big Ideas categorization
  is_big_idea: Boolean, // Default false for existing goals
  big_idea_rank: Number?, // 1-3 for ranking, null for regular destinations
  
  // ENHANCED: Progress tracking
  progress_percentage: Number, // Maintain existing
  progress_emoji: String, // Maintain existing
  progress_notes: String?,
  progress_history: [{
    emoji: String,
    notes: String?,
    percentage: Number?,
    timestamp: Date
  }],
  
  // NEW: Enhanced categorization
  priority: String, // "medium" default for existing
  category: String, // "personal" default for existing
  
  // NEW: AI and source tracking
  ai_suggested: Boolean, // false for existing goals
  source_documents: [ObjectId],
  source_entries: [ObjectId],
  
  // EXISTING: Status and metadata (maintain all)
  status: String,
  tags: [String],
  created_at: Date,
  updated_at: Date
}
```

**Migration Steps**:
1. Create new `destinations` collection
2. Copy all documents from `goals` to `destinations`
3. Rename `goal_statement` → `destination_statement`
4. Add new fields with default values
5. Create indexes on new collection
6. Update application to use `destinations` collection
7. Keep `goals` as backup during transition

### New Collections

#### 1. `quotes` Collection
```javascript
{
  _id: ObjectId,
  quote_text: String,
  author: String,
  source: String?,
  category: String, // "motivation" | "leadership" | "growth" | "courage"
  tags: [String],
  display_count: Number, // Default 0
  like_count: Number, // Default 0
  active: Boolean, // Default true
  created_by: String, // Admin user
  created_at: Date,
  updated_at: Date
}
```

#### 2. `user_quote_likes` Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  quote_id: ObjectId,
  liked_at: Date
}
```

#### 3. `small_steps` Collection
```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  step_text: String,
  completed: Boolean, // Default false
  completed_at: Date?,
  source_entry_id: ObjectId,
  ai_confidence: Number, // 0-1
  related_destination_id: ObjectId?,
  created_at: Date,
  updated_at: Date
}
```

#### 4. `coach_resources` Collection
```javascript
{
  _id: ObjectId,
  coach_user_id: ObjectId,
  title: String,
  description: String?,
  resource_url: String,
  resource_type: String, // "document" | "article" | "video" | "tool"
  is_template: Boolean, // Default false
  client_specific: Boolean, // Default false
  target_client_id: ObjectId?,
  category: String, // "exercise" | "assessment" | "reading" | "framework"
  tags: [String],
  active: Boolean, // Default true
  created_at: Date,
  updated_at: Date
}
```

#### 5. `coach_client_notes` Collection
```javascript
{
  _id: ObjectId,
  coach_user_id: ObjectId,
  client_user_id: ObjectId,
  note_of_moment: String?,
  way_of_working: String?,
  about_me: String?,
  way_of_working_template_id: ObjectId?,
  about_me_template_id: ObjectId?,
  created_at: Date,
  updated_at: Date
}
```

### Enhanced Existing Collections

#### User Profiles Enhancement
```javascript
// Add to existing profiles collection
{
  // ... existing fields maintained
  
  // NEW: Basecamp - Identity Foundation
  identity_foundation: {
    values: String?,
    energy_amplifiers: String?,
    energy_drainers: String?,
    personality_notes: String?,
    clifton_strengths: [String],
    enneagram_type: String?,
    disc_profile: Object?,
    myers_briggs: String?
  },
  
  // NEW: Freemium tracking
  freemium_status: {
    has_coach: Boolean, // Derive from existing coaching relationships
    entries_count: Number, // Count from entries collection
    max_free_entries: Number, // Default 3
    coach_requested: Boolean, // Default false
    coach_request_date: Date?
  },
  
  // NEW: Redesign preferences
  dashboard_preferences: {
    preferred_landing_tab: String, // Default "journey"
    quote_likes: [ObjectId],
    onboarding_completed: Boolean, // Default false
    tooltips_shown: Boolean // Default false
  },
  
  // NEW: Feature flags
  redesign_features: {
    unified_entries: Boolean, // Default false
    destinations_rebrand: Boolean, // Default false
    mountain_navigation: Boolean, // Default false
    freemium_gating: Boolean // Default false
  }
}
```

#### Coaching Relationships Enhancement
```javascript
// Add to existing coaching_relationship collection
{
  // ... existing fields maintained
  
  // NEW: Pending relationship support
  status: String, // "active" default for existing, "pending" | "inactive" | "declined"
  invited_by_email: String?,
  invitation_accepted_at: Date?,
  
  // NEW: Freemium transition tracking
  upgraded_from_freemium: Boolean, // Default false
  upgrade_date: Date?
}
```

## Backend Service Changes

### Service Renames and Updates

#### 1. `GoalService` → `DestinationService`
```python
# File: backend/app/services/destination_service.py (renamed from goal_service.py)

class DestinationService:
    def __init__(self):
        self.collection = db.destinations  # Updated collection reference
    
    # UPDATED: Method renames
    async def create_destination(self, destination_data):  # Was create_goal
        # Handle new fields: is_big_idea, priority, category, etc.
        pass
    
    async def get_destinations(self, user_id):  # Was get_goals
        # Return destinations with new fields
        pass
    
    async def get_three_big_ideas(self, user_id):  # NEW METHOD
        # Get destinations where is_big_idea=True, ordered by big_idea_rank
        pass
    
    async def update_destination_progress(self, destination_id, progress_data):  # Was update_goal_progress
        # Handle progress_history tracking
        pass
    
    # MAINTAIN: Backward compatibility methods
    async def create_goal(self, goal_data):  # Deprecated wrapper
        # Convert goal_data to destination_data and call create_destination
        pass
```

#### 2. New `EntryService`
```python
# File: backend/app/services/entry_service.py

class EntryService:
    def __init__(self):
        self.collection = db.entries
        self.ai_service = AIService()
    
    async def create_entry(self, entry_data):
        # Handle both session and fresh_thought types
        # Generate AI title if not provided
        # Process for goal detection
        pass
    
    async def get_entries(self, user_id, entry_type=None):
        # Filter by entry_type if provided
        # Apply freemium gating
        pass
    
    async def get_entry_insights(self, entry_id, user_id):
        # Return AI insights with freemium gating
        pass
    
    async def accept_detected_goals(self, entry_id, accepted_goals):
        # Convert accepted goals to destinations
        pass
```

#### 3. New `QuoteService`
```python
# File: backend/app/services/quote_service.py

class QuoteService:
    def __init__(self):
        self.quotes_collection = db.quotes
        self.likes_collection = db.user_quote_likes
    
    async def get_daily_quotes(self, user_id, count=5):
        # Return personalized quotes (favorites first)
        pass
    
    async def like_quote(self, user_id, quote_id):
        # Toggle like status
        pass
    
    async def get_user_favorites(self, user_id):
        # Return user's liked quotes
        pass
```

#### 4. New `FreemiumService`
```python
# File: backend/app/services/freemium_service.py

class FreemiumService:
    def __init__(self):
        self.profiles_collection = db.profiles
        self.entries_collection = db.entries
        self.coaching_relationships_collection = db.coaching_relationships
    
    async def get_freemium_status(self, user_id):
        # Check coach status and entry count
        pass
    
    async def can_create_entry(self, user_id):
        # Check if user can create new entry
        pass
    
    async def increment_entry_count(self, user_id):
        # Update entry count for freemium users
        pass
```

### API Endpoint Updates

#### 1. Destinations Endpoints (Updated from Goals)
```python
# File: backend/app/api/v1/destinations.py (renamed from goals.py)

@router.post("/destinations")  # Was /goals
async def create_destination(destination_data: DestinationCreate):
    pass

@router.get("/destinations")  # Was /goals
async def get_destinations(user_id: str):
    pass

@router.get("/destinations/three-big-ideas")  # NEW
async def get_three_big_ideas(user_id: str):
    pass

# MAINTAIN: Backward compatibility
@router.post("/goals")  # Deprecated
async def create_goal_deprecated(goal_data: GoalCreate):
    # Convert to destination format and redirect
    pass
```

#### 2. New Entries Endpoints
```python
# File: backend/app/api/v1/entries.py

@router.post("/entries")
async def create_entry(entry_data: EntryCreate):
    pass

@router.get("/entries")
async def get_entries(user_id: str, entry_type: Optional[str] = None):
    pass

@router.get("/entries/{entry_id}/insights")
async def get_entry_insights(entry_id: str, user_id: str):
    pass

@router.post("/entries/{entry_id}/accept-goals")
async def accept_detected_goals(entry_id: str, accepted_goals: AcceptedGoals):
    pass
```

## Migration Scripts

### 1. Database Migration Script
```python
# File: backend/migrations/s10_1_foundation_migration.py

async def migrate_session_insights_to_entries():
    """Migrate session_insights collection to entries with new fields"""
    # 1. Create entries collection
    # 2. Copy all documents from session_insights
    # 3. Add entry_type: "session" to all documents
    # 4. Generate titles using AI service
    # 5. Add detected_goals: [] to all documents
    # 6. Create indexes
    pass

async def migrate_goals_to_destinations():
    """Migrate goals collection to destinations with new fields"""
    # 1. Create destinations collection
    # 2. Copy all documents from goals
    # 3. Rename goal_statement to destination_statement
    # 4. Add new fields with defaults
    # 5. Create indexes
    pass

async def create_new_collections():
    """Create all new collections with indexes"""
    # 1. Create quotes collection with sample data
    # 2. Create user_quote_likes collection
    # 3. Create small_steps collection
    # 4. Create coach_resources collection
    # 5. Create coach_client_notes collection
    pass

async def enhance_existing_collections():
    """Add new fields to existing collections"""
    # 1. Add identity_foundation to profiles
    # 2. Add freemium_status to profiles
    # 3. Add dashboard_preferences to profiles
    # 4. Add redesign_features to profiles
    # 5. Add status to coaching_relationships
    pass

async def rollback_migration():
    """Rollback migration if needed"""
    # 1. Restore original collections
    # 2. Remove new collections
    # 3. Remove new fields from existing collections
    pass
```

### 2. Data Validation Script
```python
# File: backend/migrations/s10_1_validation.py

async def validate_migration():
    """Validate migration success"""
    # 1. Check document counts match
    # 2. Validate required fields exist
    # 3. Check data integrity
    # 4. Verify indexes created
    pass
```

## Testing Strategy

### 1. Migration Testing
- [ ] **Staging Environment**: Run full migration on staging data
- [ ] **Data Integrity**: Verify all documents migrated correctly
- [ ] **Performance**: Test query performance with new schema
- [ ] **Rollback**: Test rollback procedures

### 2. API Testing
- [ ] **Backward Compatibility**: Ensure existing endpoints still work
- [ ] **New Endpoints**: Test all new API endpoints
- [ ] **Error Handling**: Test error scenarios and edge cases
- [ ] **Performance**: Load testing with new endpoints

### 3. Service Testing
- [ ] **Unit Tests**: Update existing tests for renamed services
- [ ] **Integration Tests**: Test service interactions
- [ ] **Mock Data**: Create test data for new collections

## Deployment Plan

### Phase 1: Database Migration (Week 1)
1. **Day 1-2**: Create migration scripts and test in development
2. **Day 3-4**: Run migration in staging environment
3. **Day 5**: Validate migration and performance testing

### Phase 2: Backend Updates (Week 2)
1. **Day 1-2**: Update services and create new services
2. **Day 3-4**: Update API endpoints with backward compatibility
3. **Day 5**: Integration testing and deployment preparation

### Phase 3: Production Deployment
1. **Maintenance Window**: Run migration scripts
2. **Gradual Rollout**: Deploy backend changes with feature flags
3. **Monitoring**: Monitor performance and error rates
4. **Validation**: Verify migration success in production

## Success Criteria

### Technical Success
- [ ] All collections successfully migrated with 100% data integrity
- [ ] New collections created and populated with initial data
- [ ] All existing API endpoints maintain backward compatibility
- [ ] New API endpoints functional and tested
- [ ] Performance metrics maintained or improved

### Business Success
- [ ] Zero downtime during migration
- [ ] No data loss or corruption
- [ ] Existing user workflows unaffected
- [ ] Foundation ready for subsequent sprints

## Risk Mitigation

### Data Loss Prevention
- [ ] **Full Backups**: Complete database backup before migration
- [ ] **Rollback Scripts**: Tested rollback procedures
- [ ] **Staging Validation**: Full migration testing in staging

### Performance Risks
- [ ] **Index Optimization**: Proper indexes on new collections
- [ ] **Query Optimization**: Efficient queries for new schema
- [ ] **Monitoring**: Real-time performance monitoring

### Compatibility Risks
- [ ] **API Versioning**: Maintain v1 endpoints during transition
- [ ] **Gradual Migration**: Feature flags for gradual rollout
- [ ] **Fallback Options**: Ability to revert to old schema if needed

## Dependencies

### Internal Dependencies
- AI Service for title generation and goal detection
- Existing user authentication system
- Current database infrastructure

### External Dependencies
- MongoDB migration tools
- Staging environment availability
- Deployment pipeline updates

## Next Steps After Sprint Completion

1. **Validate Migration**: Comprehensive validation of all changes
2. **Update Documentation**: Update API documentation and schemas
3. **Prepare Sprint S10.2**: Begin work on landing page and quote system
4. **Monitor Performance**: Ongoing monitoring of new schema performance
5. **Gather Feedback**: Collect feedback from development team

---

**Sprint S10.1 establishes the critical foundation for the entire redesign project. Success here ensures smooth implementation of all subsequent sprints.**