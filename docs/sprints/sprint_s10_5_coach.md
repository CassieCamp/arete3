# Sprint S10.5: Coach Features & Freemium

**Epic**: [Sprint S10 Application Redesign](./sprint_s10_redesign_epic.md)  
**Duration**: 2 weeks  
**Priority**: Medium  
**Dependencies**: Sprint S10.1 (Foundation), Sprint S10.2 (Landing), Sprint S10.3 (Entries), Sprint S10.4 (Mountain)

## Sprint Overview

This sprint implements coach-specific features including the coach dashboard, resource management, client-specific content, and enhanced onboarding flows. It also completes the freemium system with upgrade paths and coach request handling.

## Sprint Goals

1. **Build coach dashboard** with client management and overview
2. **Implement coach resource library** with templates and client-specific content
3. **Create client-specific coach content** (note of moment, way of working, about me)
4. **Enhance onboarding flows** for both coaches and clients
5. **Complete freemium upgrade paths** and coach request system

## Wireframe Reference

Based on wireframe analysis:
- **Coach dashboard** with client list and management tools
- **Resource library** with categorized coaching materials
- **Client-specific content** customization for coaches
- **Enhanced onboarding** with organization lookup and role-based flows
- **Freemium upgrade prompts** throughout the application

## Frontend Components

### 1. Coach Dashboard
```typescript
// File: frontend/src/app/dashboard/coach/page.tsx

export default function CoachDashboard() {
  const [clients, setClients] = useState<CoachClient[]>([]);
  const [resources, setResources] = useState<CoachResource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'clients' | 'resources' | 'templates'>('clients');
  
  useEffect(() => {
    loadCoachData();
  }, []);
  
  const loadCoachData = async () => {
    try {
      const [clientsResponse, resourcesResponse] = await Promise.all([
        fetch('/api/v1/coach/clients'),
        fetch('/api/v1/coach/resources')
      ]);
      
      const clientsData = await clientsResponse.json();
      const resourcesData = await resourcesResponse.json();
      
      setClients(clientsData.clients);
      setResources(resourcesData.resources);
    } catch (error) {
      console.error('Failed to load coach data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <CoachDashboardSkeleton />;
  }
  
  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Coach Dashboard</h1>
        <p className="text-gray-600">
          Manage your clients, resources, and coaching materials.
        </p>
      </div>
      
      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex space-x-8">
          {[
            { id: 'clients', label: 'Clients', count: clients.length },
            { id: 'resources', label: 'Resources', count: resources.length },
            { id: 'templates', label: 'Templates', count: resources.filter(r => r.is_template).length }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
              <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                {tab.count}
              </span>
            </button>
          ))}
        </nav>
      </div>
      
      {/* Tab Content */}
      {activeTab === 'clients' && (
        <ClientManagement 
          clients={clients}
          onUpdate={loadCoachData}
        />
      )}
      
      {activeTab === 'resources' && (
        <ResourceManagement 
          resources={resources.filter(r => !r.is_template)}
          onUpdate={loadCoachData}
        />
      )}
      
      {activeTab === 'templates' && (
        <TemplateManagement 
          templates={resources.filter(r => r.is_template)}
          onUpdate={loadCoachData}
        />
      )}
    </div>
  );
}
```

### 2. Client Management Component
```typescript
// File: frontend/src/components/coach/ClientManagement.tsx

interface ClientManagementProps {
  clients: CoachClient[];
  onUpdate: () => void;
}

export function ClientManagement({ clients, onUpdate }: ClientManagementProps) {
  const [selectedClient, setSelectedClient] = useState<CoachClient | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  
  const activeClients = clients.filter(c => c.relationship_status === 'active');
  const pendingClients = clients.filter(c => c.relationship_status === 'pending');
  
  return (
    <div className="space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Clients</p>
              <p className="text-2xl font-semibold text-gray-900">{activeClients.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending Invites</p>
              <p className="text-2xl font-semibold text-gray-900">{pendingClients.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Entries</p>
              <p className="text-2xl font-semibold text-gray-900">
                {activeClients.reduce((sum, client) => sum + client.entries_count, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Client List</h2>
        <button
          onClick={() => setShowInviteModal(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 inline mr-2" />
          Invite Client
        </button>
      </div>
      
      {/* Pending Invitations */}
      {pendingClients.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
          <h3 className="font-medium text-orange-800 mb-2">Pending Invitations</h3>
          <div className="space-y-2">
            {pendingClients.map((client) => (
              <div key={client.id} className="flex items-center justify-between bg-white rounded p-3">
                <div>
                  <div className="font-medium text-gray-800">{client.email}</div>
                  <div className="text-sm text-gray-600">
                    Invited {new Date(client.created_at).toLocaleDateString()}
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">
                    Resend
                  </button>
                  <button className="text-red-600 hover:text-red-800 text-sm">
                    Cancel
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Active Clients */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6">
          {activeClients.length === 0 ? (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-600 mb-2">No active clients yet</h3>
              <p className="text-gray-500 mb-4">Invite your first client to get started.</p>
              <button
                onClick={() => setShowInviteModal(true)}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Invite Client
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {activeClients.map((client) => (
                <ClientCard
                  key={client.id}
                  client={client}
                  onClick={() => setSelectedClient(client)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Client Details Modal */}
      {selectedClient && (
        <ClientDetailsModal
          client={selectedClient}
          isOpen={!!selectedClient}
          onClose={() => setSelectedClient(null)}
          onUpdate={onUpdate}
        />
      )}
      
      {/* Invite Client Modal */}
      {showInviteModal && (
        <InviteClientModal
          isOpen={showInviteModal}
          onClose={() => setShowInviteModal(false)}
          onSuccess={onUpdate}
        />
      )}
    </div>
  );
}
```

### 3. Client Details Modal
```typescript
// File: frontend/src/components/coach/ClientDetailsModal.tsx

interface ClientDetailsModalProps {
  client: CoachClient;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export function ClientDetailsModal({ client, isOpen, onClose, onUpdate }: ClientDetailsModalProps) {
  const [clientNotes, setClientNotes] = useState({
    note_of_moment: '',
    way_of_working: '',
    about_me: ''
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'notes' | 'resources'>('overview');
  
  useEffect(() => {
    if (isOpen) {
      loadClientNotes();
    }
  }, [isOpen, client.id]);
  
  const loadClientNotes = async () => {
    try {
      const response = await fetch(`/api/v1/coach/clients/${client.id}/notes`);
      const data = await response.json();
      setClientNotes(data.notes || {
        note_of_moment: '',
        way_of_working: '',
        about_me: ''
      });
    } catch (error) {
      console.error('Failed to load client notes:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const saveClientNotes = async () => {
    setIsSaving(true);
    try {
      await fetch(`/api/v1/coach/clients/${client.id}/notes`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(clientNotes)
      });
      
      showSuccessToast('Client notes saved successfully');
      onUpdate();
    } catch (error) {
      console.error('Failed to save client notes:', error);
      showErrorToast('Failed to save notes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold">{client.name}</h2>
            <p className="text-gray-600">{client.email}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        {/* Tab Navigation */}
        <div className="border-b">
          <nav className="flex px-6">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'notes', label: 'Client Notes' },
              { id: 'resources', label: 'Resources' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-4 px-4 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
        
        {/* Tab Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'overview' && (
            <ClientOverview client={client} />
          )}
          
          {activeTab === 'notes' && (
            <ClientNotesEditor
              notes={clientNotes}
              onChange={setClientNotes}
              onSave={saveClientNotes}
              isLoading={isLoading}
              isSaving={isSaving}
            />
          )}
          
          {activeTab === 'resources' && (
            <ClientResources clientId={client.id} />
          )}
        </div>
      </div>
    </div>
  );
}
```

### 4. Client Notes Editor
```typescript
// File: frontend/src/components/coach/ClientNotesEditor.tsx

interface ClientNotesEditorProps {
  notes: ClientNotes;
  onChange: (notes: ClientNotes) => void;
  onSave: () => void;
  isLoading: boolean;
  isSaving: boolean;
}

export function ClientNotesEditor({ notes, onChange, onSave, isLoading, isSaving }: ClientNotesEditorProps) {
  const [hasChanges, setHasChanges] = useState(false);
  
  const handleChange = (field: keyof ClientNotes, value: string) => {
    onChange({ ...notes, [field]: value });
    setHasChanges(true);
  };
  
  const handleSave = () => {
    onSave();
    setHasChanges(false);
  };
  
  if (isLoading) {
    return <div className="animate-pulse space-y-4">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="h-32 bg-gray-200 rounded"></div>
      ))}
    </div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-gray-800">Client-Specific Content</h3>
        {hasChanges && (
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
          >
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        )}
      </div>
      
      {/* Note of the Moment */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Note of the Moment
        </label>
        <p className="text-xs text-gray-500 mb-2">
          A current message or encouragement for this client (visible to them)
        </p>
        <textarea
          value={notes.note_of_moment}
          onChange={(e) => handleChange('note_of_moment', e.target.value)}
          placeholder="e.g., 'Great progress on your leadership goals this week!'"
          className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <div className="mt-1 text-xs text-gray-500">
          {notes.note_of_moment.length}/500 characters
        </div>
      </div>
      
      {/* Way of Working */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Way of Working
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Your coaching approach and methodology for this specific client
        </p>
        <textarea
          value={notes.way_of_working}
          onChange={(e) => handleChange('way_of_working', e.target.value)}
          placeholder="e.g., 'I focus on strengths-based coaching with weekly check-ins and goal setting...'"
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <div className="mt-1 text-xs text-gray-500">
          {notes.way_of_working.length}/1000 characters
        </div>
      </div>
      
      {/* About Me */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          About Me (for this client)
        </label>
        <p className="text-xs text-gray-500 mb-2">
          Personalized introduction and background relevant to this client
        </p>
        <textarea
          value={notes.about_me}
          onChange={(e) => handleChange('about_me', e.target.value)}
          placeholder="e.g., 'As someone who has also navigated leadership transitions in tech...'"
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
        <div className="mt-1 text-xs text-gray-500">
          {notes.about_me.length}/1000 characters
        </div>
      </div>
      
      {/* Templates Section */}
      <div className="border-t pt-6">
        <h4 className="font-medium text-gray-800 mb-3">Use Templates</h4>
        <p className="text-sm text-gray-600 mb-4">
          Apply content from your saved templates to quickly populate these fields.
        </p>
        <div className="flex space-x-2">
          <button className="text-blue-600 hover:text-blue-800 text-sm border border-blue-300 px-3 py-1 rounded">
            Apply Way of Working Template
          </button>
          <button className="text-blue-600 hover:text-blue-800 text-sm border border-blue-300 px-3 py-1 rounded">
            Apply About Me Template
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 5. Enhanced Onboarding Flow
```typescript
// File: frontend/src/components/onboarding/EnhancedOnboardingFlow.tsx

interface EnhancedOnboardingFlowProps {
  userType: 'coach' | 'client';
}

export function EnhancedOnboardingFlow({ userType }: EnhancedOnboardingFlowProps) {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    organization: '',
    email: '',
    role: userType,
    client_invitations: [] as string[],
    coach_association_accepted: false,
    coach_referral_opt_in: false
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [organizationSuggestion, setOrganizationSuggestion] = useState('');
  
  const totalSteps = userType === 'coach' ? 4 : 3;
  
  useEffect(() => {
    if (userType === 'coach' && formData.email) {
      suggestOrganization();
    }
  }, [formData.email, userType]);
  
  const suggestOrganization = async () => {
    try {
      const response = await fetch('/api/v1/onboarding/organization-lookup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: formData.email })
      });
      
      const data = await response.json();
      if (data.suggested_organization) {
        setOrganizationSuggestion(data.suggested_organization);
        setFormData(prev => ({ 
          ...prev, 
          organization: data.suggested_organization 
        }));
      }
    } catch (error) {
      console.error('Failed to suggest organization:', error);
    }
  };
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const endpoint = userType === 'coach' 
        ? '/api/v1/onboarding/complete-coach'
        : '/api/v1/onboarding/complete-client';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        throw new Error('Failed to complete onboarding');
      }
    } catch (error) {
      console.error('Onboarding error:', error);
      showErrorToast('Failed to complete onboarding. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg max-w-md w-full p-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>Step {step} of {totalSteps}</span>
            <span>{Math.round((step / totalSteps) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / totalSteps) * 100}%` }}
            ></div>
          </div>
        </div>
        
        {/* Step Content */}
        {step === 1 && (
          <OnboardingStep1
            userType={userType}
            formData={formData}
            onChange={setFormData}
            onNext={() => setStep(2)}
          />
        )}
        
        {step === 2 && (
          <OnboardingStep2
            userType={userType}
            formData={formData}
            onChange={setFormData}
            organizationSuggestion={organizationSuggestion}
            onNext={() => setStep(3)}
            onBack={() => setStep(1)}
          />
        )}
        
        {step === 3 && userType === 'coach' && (
          <OnboardingStep3Coach
            formData={formData}
            onChange={setFormData}
            onNext={() => setStep(4)}
            onBack={() => setStep(2)}
          />
        )}
        
        {step === 3 && userType === 'client' && (
          <OnboardingStep3Client
            formData={formData}
            onChange={setFormData}
            onSubmit={handleSubmit}
            onBack={() => setStep(2)}
            isSubmitting={isSubmitting}
          />
        )}
        
        {step === 4 && userType === 'coach' && (
          <OnboardingStep4Coach
            formData={formData}
            onChange={setFormData}
            onSubmit={handleSubmit}
            onBack={() => setStep(3)}
            isSubmitting={isSubmitting}
          />
        )}
      </div>
    </div>
  );
}
```

### 6. Freemium Upgrade Components
```typescript
// File: frontend/src/components/freemium/UpgradePrompts.tsx

interface UpgradePromptProps {
  context: 'entry_limit' | 'feature_lock' | 'insights_limit';
  freemiumStatus: FreemiumStatus;
}

export function UpgradePrompt({ context, freemiumStatus }: UpgradePromptProps) {
  const [showRequestForm, setShowRequestForm] = useState(false);
  
  const prompts = {
    entry_limit: {
      title: 'Unlock Unlimited Entries',
      description: 'You\'ve reached your free entry limit. Connect with a coach to continue your journey.',
      benefits: [
        'Unlimited session and thought entries',
        'Advanced AI insights and analysis',
        'Goal tracking and progress monitoring',
        'Personalized coaching resources'
      ]
    },
    feature_lock: {
      title: 'Premium Feature',
      description: 'This feature is available with coach access. Unlock your full potential.',
      benefits: [
        'Access to all premium features',
        'Personalized coaching guidance',
        'Advanced analytics and insights',
        'Priority support'
      ]
    },
    insights_limit: {
      title: 'Deeper Insights Available',
      description: 'Get more detailed AI analysis and coaching insights with a coach.',
      benefits: [
        'Comprehensive AI analysis',
        'Coaching-specific insights',
        'Progress tracking over time',
        'Personalized recommendations'
      ]
    }
  };
  
  const prompt = prompts[context];
  
  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
      <div className="flex items-start space-x-4">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Sparkles className="w-6 h-6 text-blue-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            {prompt.title}
          </h3>
          <p className="text-gray-600 mb-4">
            {prompt.description}
          </p>
          
          <div className="mb-4">
            <h4 className="font-medium text-gray-800 mb-2">What you'll get:</h4>
            <ul className="space-y-1">
              {prompt.benefits.map((benefit, index) => (
                <li key={index} className="flex items-center text-sm text-gray-700">
                  <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                  {benefit}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => setShowRequestForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Request Coach Access
            </button>
            <button className="text-blue-600 hover:text-blue-800 text-sm">
              Learn More
            </button>
          </div>
        </div>
      </div>
      
      {showRequestForm && (
        <CoachRequestModal
          isOpen={showRequestForm}
          onClose={() => setShowRequestForm(false)}
          context={context}
        />
      )}
    </div>
  );
}
```

## Backend Implementation

### 1. Coach Dashboard API
```python
# File: backend/app/api/v1/coach.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.coach_service import CoachService
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/coach/clients")
async def get_coach_clients(
    current_user = Depends(get_current_user)
):
    """Get coach's client list with stats"""
    coach_service = CoachService()
    clients = await coach_service.get_coach_clients(current_user.id)
    return {"clients": clients}

@router.get("/coach/clients/{client_id}/notes")
async def get_client_notes(
    client_id: str,
    current_user = Depends(get_current_user)
):
    """Get coach's notes for specific client"""
    coach_service = CoachService()
    notes = await coach_service.get_client_notes(current_user.id, client_id)
    return {"notes": notes}

@router.put("/coach