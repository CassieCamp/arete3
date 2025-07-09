# Sprint S9: Unpaired Client Insights Implementation Plan

## Objective

Enable clients to upload session transcripts and generate AI-powered insights without requiring an active coaching relationship. These insights should be full-featured, private to the client by default, but shareable with coaches when relationships are established later.

## Background

Currently, the session insights feature requires an active coaching relationship (`coaching_relationship_id`) to create insights. The system validates that users are part of a coaching relationship before allowing transcript uploads. This creates a barrier for:

1. **New clients** who want to explore the platform's capabilities before connecting with a coach
2. **Independent users** who want self-reflection tools without formal coaching
3. **Existing clients** who want to continue using insights between coaching relationships

The current implementation in [`SessionInsightService.create_insight_from_transcript()`](backend/app/services/session_insight_service.py:28) validates coaching relationships and requires both `coach_user_id` and `client_user_id` fields in the [`SessionInsight`](backend/app/models/session_insight.py:125) model.

## Proposed Changes

### Backend

#### Database Schema Changes

**SessionInsight Model Updates** ([`backend/app/models/session_insight.py`](backend/app/models/session_insight.py)):

```python
# Make coaching relationship fields optional for unpaired insights
coaching_relationship_id: Optional[str] = None  # Currently required
coach_user_id: Optional[str] = None  # Currently required
client_user_id: str  # Keep required - always the insight owner

# Add new fields for unpaired insights
is_unpaired: bool = False  # Flag to identify unpaired insights
shared_with_coaches: List[str] = Field(default_factory=list)  # Coach user IDs with access
sharing_permissions: Dict[str, Any] = Field(default_factory=dict)  # Granular permissions
```

**New Sharing Model** (create [`backend/app/models/insight_sharing.py`](backend/app/models/insight_sharing.py)):

```python
class InsightSharingPermission(BaseModel):
    insight_id: str
    client_user_id: str
    coach_user_id: str
    granted_at: datetime
    permissions: Dict[str, bool]  # view, comment, export, etc.
    revoked_at: Optional[datetime] = None
```

#### API Endpoints

**New Endpoints** in [`backend/app/api/v1/endpoints/session_insights.py`](backend/app/api/v1/endpoints/session_insights.py):

```python
@router.post("/unpaired", response_model=SessionInsightResponse)
async def create_unpaired_session_insight_from_file(
    session_date: Optional[str] = Form(None),
    session_title: Optional[str] = Form(None),
    transcript_file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_clerk_id)
)

@router.post("/unpaired/from-text", response_model=SessionInsightResponse)
async def create_unpaired_session_insight_from_text(
    request: UnpairedSessionInsightCreateRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
)

@router.get("/my-insights", response_model=List[SessionInsightResponse])
async def get_my_insights(
    include_unpaired: bool = True,
    limit: int = 20,
    offset: int = 0,
    current_user_id: str = Depends(get_current_user_clerk_id)
)

@router.post("/{insight_id}/share", response_model=Dict[str, str])
async def share_insight_with_coach(
    insight_id: str,
    request: ShareInsightRequest,
    current_user_id: str = Depends(get_current_user_clerk_id)
)

@router.delete("/{insight_id}/share/{coach_user_id}")
async def revoke_insight_sharing(
    insight_id: str,
    coach_user_id: str,
    current_user_id: str = Depends(get_current_user_clerk_id)
)
```

#### Service Layer Changes

**SessionInsightService Updates** ([`backend/app/services/session_insight_service.py`](backend/app/services/session_insight_service.py)):

```python
async def create_unpaired_insight_from_transcript(
    self,
    client_user_id: str,
    transcript_content: str,
    session_date: Optional[str] = None,
    session_title: Optional[str] = None,
    source_document_id: Optional[str] = None
) -> SessionInsight

async def get_user_insights(
    self,
    user_id: str,
    include_unpaired: bool = True,
    include_paired: bool = True,
    limit: int = 20,
    offset: int = 0
) -> List[SessionInsight]

async def share_insight_with_coach(
    self,
    insight_id: str,
    client_user_id: str,
    coach_user_id: str,
    permissions: Dict[str, bool]
) -> bool

async def get_shared_insights_for_coach(
    self,
    coach_user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[SessionInsight]
```

#### Repository Updates

**SessionInsightRepository Updates** ([`backend/app/repositories/session_insight_repository.py`](backend/app/repositories/session_insight_repository.py)):

```python
async def get_insights_by_user(
    self,
    user_id: str,
    include_unpaired: bool = True,
    include_paired: bool = True,
    limit: int = 20,
    offset: int = 0
) -> List[SessionInsight]

async def get_shared_insights_for_coach(
    self,
    coach_user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[SessionInsight]

async def update_sharing_permissions(
    self,
    insight_id: str,
    shared_with_coaches: List[str]
) -> bool
```

#### Schema Updates

**New Schemas** ([`backend/app/schemas/session_insight.py`](backend/app/schemas/session_insight.py)):

```python
class UnpairedSessionInsightCreateRequest(BaseModel):
    session_date: Optional[str] = None
    session_title: Optional[str] = None
    transcript_text: str

class ShareInsightRequest(BaseModel):
    coach_user_id: str
    permissions: Dict[str, bool] = {
        "view": True,
        "comment": False,
        "export": False
    }

class MyInsightsResponse(BaseModel):
    paired_insights: List[SessionInsightResponse]
    unpaired_insights: List[SessionInsightResponse]
    total_count: int
```

### Frontend

#### New UI Components

**Unpaired Insights Upload Component** (create [`frontend/src/components/insights/UnpairedInsightUpload.tsx`](frontend/src/components/insights/UnpairedInsightUpload.tsx)):
- Similar to existing insight submission but without relationship selection
- Clear messaging about unpaired nature
- Option to share with coaches later

**My Insights Dashboard** (create [`frontend/src/components/insights/MyInsightsDashboard.tsx`](frontend/src/components/insights/MyInsightsDashboard.tsx)):
- Tabbed interface: "All Insights", "Paired", "Unpaired"
- Sharing controls for unpaired insights
- Visual indicators for sharing status

**Insight Sharing Modal** (create [`frontend/src/components/insights/InsightSharingModal.tsx`](frontend/src/components/insights/InsightSharingModal.tsx)):
- Coach selection from user's relationships
- Permission granularity controls
- Sharing history and revocation

#### Page Updates

**Insights Page Redesign** ([`frontend/src/app/dashboard/insights/page.tsx`](frontend/src/app/dashboard/insights/page.tsx)):

```typescript
// New flow logic
const [currentView, setCurrentView] = useState<
  'my-insights' | 'relationship-insights' | 'upload-unpaired' | 'detail'
>('my-insights');

// Add unpaired insights support
const handleUnpairedUpload = () => {
  setCurrentView('upload-unpaired');
};
```

**Navigation Updates**:
- Add "My Insights" as primary entry point
- Keep "Relationship Insights" for paired insights
- Add "Upload Session" for unpaired insights

#### Service Layer Updates

**Session Insight Service** ([`frontend/src/services/sessionInsightService.ts`](frontend/src/services/sessionInsightService.ts)):

```typescript
async createUnpairedInsightFromFile(
  token: string,
  file: File,
  sessionDate?: string,
  sessionTitle?: string
): Promise<SessionInsight>

async createUnpairedInsightFromText(
  token: string,
  transcriptText: string,
  sessionDate?: string,
  sessionTitle?: string
): Promise<SessionInsight>

async getMyInsights(
  token: string,
  includeUnpaired: boolean = true,
  limit: number = 20,
  offset: number = 0
): Promise<MyInsightsResponse>

async shareInsightWithCoach(
  token: string,
  insightId: string,
  coachUserId: string,
  permissions: Record<string, boolean>
): Promise<void>
```

## Out of Scope

1. **Bulk sharing operations** - Individual insight sharing only
2. **Advanced permission management** - Basic view/share permissions only
3. **Insight collaboration features** - No commenting or co-editing
4. **Insight templates or categories** - Use existing insight structure
5. **Integration with external calendar systems** - Manual session date entry only
6. **Automated coach recommendations** - Manual coach selection for sharing
7. **Insight analytics or reporting** - Basic insight viewing only

## Action Plan

### Phase 1: Backend Foundation (Days 1-3)

1. **Database Schema Updates**
   - [ ] Update [`SessionInsight`](backend/app/models/session_insight.py:125) model to support optional relationship fields
   - [ ] Add `is_unpaired`, `shared_with_coaches` fields
   - [ ] Create migration script for existing data
   - [ ] Test schema changes with existing insights

2. **Core Service Logic**
   - [ ] Implement [`create_unpaired_insight_from_transcript()`](backend/app/services/session_insight_service.py) method
   - [ ] Update AI analysis to work without coaching context
   - [ ] Add insight sharing logic
   - [ ] Update repository methods for unpaired insights

3. **API Endpoints**
   - [ ] Create `/unpaired` and `/unpaired/from-text` endpoints
   - [ ] Implement `/my-insights` endpoint
   - [ ] Add sharing endpoints (`/share`, `/share/{coach_id}`)
   - [ ] Update existing endpoints to handle unpaired insights

### Phase 2: Frontend Core Features (Days 4-6)

4. **Upload Interface**
   - [ ] Create [`UnpairedInsightUpload`](frontend/src/components/insights/UnpairedInsightUpload.tsx) component
   - [ ] Integrate with existing file upload patterns
   - [ ] Add clear messaging about unpaired nature
   - [ ] Implement error handling and validation

5. **My Insights Dashboard**
   - [ ] Create [`MyInsightsDashboard`](frontend/src/components/insights/MyInsightsDashboard.tsx) component
   - [ ] Implement tabbed interface (All/Paired/Unpaired)
   - [ ] Add filtering and sorting capabilities
   - [ ] Show sharing status indicators

6. **Navigation Updates**
   - [ ] Update [`insights/page.tsx`](frontend/src/app/dashboard/insights/page.tsx) with new flow
   - [ ] Add "My Insights" as primary entry point
   - [ ] Maintain backward compatibility with existing flows

### Phase 3: Sharing Features (Days 7-8)

7. **Sharing Interface**
   - [ ] Create [`InsightSharingModal`](frontend/src/components/insights/InsightSharingModal.tsx) component
   - [ ] Implement coach selection from relationships
   - [ ] Add permission controls (view/export)
   - [ ] Show sharing history and revocation options

8. **Coach Experience**
   - [ ] Update coach insights view to show shared insights
   - [ ] Add visual indicators for shared vs. relationship insights
   - [ ] Implement access controls based on sharing permissions

### Phase 4: Integration & Testing (Days 9-10)

9. **Service Integration**
   - [ ] Update [`sessionInsightService.ts`](frontend/src/services/sessionInsightService.ts) with new methods
   - [ ] Implement error handling for sharing operations
   - [ ] Add loading states and user feedback

10. **Testing & Validation**
    - [ ] Test unpaired insight creation flow
    - [ ] Validate sharing permissions work correctly
    - [ ] Test backward compatibility with existing insights
    - [ ] Verify coach access to shared insights
    - [ ] Test edge cases (no relationships, sharing revocation)

### Phase 5: Polish & Documentation (Days 11-12)

11. **User Experience Polish**
    - [ ] Add onboarding tooltips for new features
    - [ ] Improve error messages and validation feedback
    - [ ] Optimize loading states and transitions
    - [ ] Add confirmation dialogs for sharing actions

12. **Documentation & Deployment**
    - [ ] Update API documentation
    - [ ] Create user guide for unpaired insights
    - [ ] Add database migration scripts
    - [ ] Prepare deployment checklist

## Implementation Considerations

### Security & Privacy
- Unpaired insights are private by default
- Sharing requires explicit user action
- Coaches can only access insights explicitly shared with them
- Sharing can be revoked at any time

### Performance
- Index on `client_user_id` and `is_unpaired` fields
- Paginate insight lists to handle large volumes
- Cache sharing permissions for frequently accessed insights

### User Experience
- Clear visual distinction between paired and unpaired insights
- Intuitive sharing controls with clear permissions
- Seamless transition from unpaired to paired when relationships form

### Backward Compatibility
- Existing insights remain unchanged
- Current relationship-based flows continue to work
- No breaking changes to existing API endpoints

## Success Metrics

1. **Adoption**: Number of unpaired insights created per week
2. **Engagement**: Time spent viewing unpaired insights
3. **Conversion**: Percentage of unpaired users who later form coaching relationships
4. **Sharing**: Number of insights shared with coaches
5. **Retention**: User return rate after creating unpaired insights

## Risk Mitigation

1. **Data Migration**: Test schema changes thoroughly with production data backup
2. **Performance Impact**: Monitor database performance with new queries
3. **User Confusion**: Provide clear onboarding and help documentation
4. **Privacy Concerns**: Implement robust access controls and audit logging
5. **Feature Complexity**: Start with MVP sharing features, iterate based on feedback