# Sprint S10.4: Mountain Navigation

**Epic**: [Sprint S10 Application Redesign](./sprint_s10_redesign_epic.md)  
**Duration**: 2 weeks  
**Priority**: High  
**Dependencies**: Sprint S10.1 (Foundation), Sprint S10.2 (Landing), Sprint S10.3 (Entries)

## Sprint Overview

This sprint implements the Mountain section with three-tab navigation: Basecamp (identity foundation), Journey (timeline), and Destinations (goals management). It includes AI assistance for identity foundation, timeline visualization, and the "Three Big Ideas" destination system.

## Sprint Goals

1. **Implement three-tab Mountain navigation** (Basecamp/Journey/Destinations)
2. **Build Basecamp identity foundation** with AI chat assistance
3. **Create Journey timeline** with unified entry display
4. **Develop Destinations management** with Three Big Ideas system
5. **Add AI-powered small steps** generation and management

## Wireframe Reference

Based on wireframe analysis:
- **Three-tab interface** at top of Mountain section
- **Basecamp tab**: Identity foundation form with AI assistance
- **Journey tab**: Vertical timeline with entry cards
- **Destinations tab**: Three Big Ideas + Small Steps list
- **AI chat integration** for identity foundation guidance

## Frontend Components

### 1. Mountain Tab Navigation
```typescript
// File: frontend/src/components/mountain/MountainTabNavigation.tsx

interface MountainTabNavigationProps {
  activeTab: 'basecamp' | 'journey' | 'destinations';
  onTabChange: (tab: 'basecamp' | 'journey' | 'destinations') => void;
}

export function MountainTabNavigation({ activeTab, onTabChange }: MountainTabNavigationProps) {
  const tabs = [
    {
      id: 'basecamp' as const,
      label: 'Basecamp',
      icon: Home,
      description: 'Your identity foundation'
    },
    {
      id: 'journey' as const,
      label: 'Journey',
      icon: Map,
      description: 'Your timeline and progress'
    },
    {
      id: 'destinations' as const,
      label: 'Destinations',
      icon: Target,
      description: 'Your goals and aspirations'
    }
  ];
  
  return (
    <div className="border-b border-gray-200 bg-white sticky top-0 z-10">
      <div className="flex">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`flex-1 py-4 px-6 text-center transition-all duration-200 ${
                isActive
                  ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
              }`}
            >
              <div className="flex flex-col items-center space-y-1">
                <Icon className={`w-5 h-5 ${isActive ? 'text-blue-600' : 'text-gray-500'}`} />
                <span className="font-medium text-sm">{tab.label}</span>
                <span className="text-xs text-gray-500 hidden sm:block">
                  {tab.description}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
```

### 2. Basecamp Tab Component
```typescript
// File: frontend/src/components/mountain/BasecampTab.tsx

interface BasecampTabProps {
  userId: string;
}

export function BasecampTab({ userId }: BasecampTabProps) {
  const [identityFoundation, setIdentityFoundation] = useState({
    values: '',
    energy_amplifiers: '',
    energy_drainers: '',
    personality_notes: ''
  });
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [showAIAssistant, setShowAIAssistant] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  
  useEffect(() => {
    loadIdentityFoundation();
  }, [userId]);
  
  const loadIdentityFoundation = async () => {
    try {
      const response = await fetch(`/api/v1/basecamp?user_id=${userId}`);
      const data = await response.json();
      setIdentityFoundation(data.identity_foundation || {
        values: '',
        energy_amplifiers: '',
        energy_drainers: '',
        personality_notes: ''
      });
    } catch (error) {
      console.error('Failed to load identity foundation:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const saveIdentityFoundation = async () => {
    setIsSaving(true);
    try {
      await fetch('/api/v1/basecamp', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(identityFoundation)
      });
    } catch (error) {
      console.error('Failed to save identity foundation:', error);
    } finally {
      setIsSaving(false);
    }
  };
  
  const sections = [
    {
      key: 'values',
      title: 'Core Values',
      description: 'What principles guide your decisions and actions?',
      placeholder: 'e.g., Integrity, Growth, Connection, Excellence...',
      icon: Heart
    },
    {
      key: 'energy_amplifiers',
      title: 'Energy Amplifiers',
      description: 'What activities, people, or environments energize you?',
      placeholder: 'e.g., Creative projects, meaningful conversations, nature...',
      icon: Zap
    },
    {
      key: 'energy_drainers',
      title: 'Energy Drainers',
      description: 'What depletes your energy or motivation?',
      placeholder: 'e.g., Micromanagement, repetitive tasks, conflict...',
      icon: Battery
    },
    {
      key: 'personality_notes',
      title: 'Personality Notes',
      description: 'Insights about your personality, strengths, and preferences',
      placeholder: 'e.g., Introvert who loves deep conversations, detail-oriented...',
      icon: User
    }
  ];
  
  if (isLoading) {
    return <BasecampSkeleton />;
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Your Basecamp</h1>
        <p className="text-gray-600">
          Build your identity foundation. Understanding yourself is the first step to meaningful growth.
        </p>
      </div>
      
      <div className="space-y-8">
        {sections.map((section) => {
          const Icon = section.icon;
          const isActive = activeSection === section.key;
          
          return (
            <div
              key={section.key}
              className={`bg-white rounded-xl border-2 transition-all duration-200 ${
                isActive ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${
                      isActive ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">
                        {section.title}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {section.description}
                      </p>
                    </div>
                  </div>
                  
                  <button
                    onClick={() => {
                      setActiveSection(section.key);
                      setShowAIAssistant(true);
                    }}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="Get AI assistance"
                  >
                    <Sparkles className="w-5 h-5" />
                  </button>
                </div>
                
                <textarea
                  value={identityFoundation[section.key as keyof typeof identityFoundation]}
                  onChange={(e) => {
                    setIdentityFoundation(prev => ({
                      ...prev,
                      [section.key]: e.target.value
                    }));
                    setActiveSection(section.key);
                  }}
                  onFocus={() => setActiveSection(section.key)}
                  onBlur={() => {
                    setActiveSection(null);
                    saveIdentityFoundation();
                  }}
                  placeholder={section.placeholder}
                  className="w-full h-32 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                />
                
                <div className="mt-2 text-xs text-gray-500">
                  {identityFoundation[section.key as keyof typeof identityFoundation].length} characters
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* AI Assistant Modal */}
      {showAIAssistant && activeSection && (
        <AIAssistanceModal
          isOpen={showAIAssistant}
          onClose={() => setShowAIAssistant(false)}
          section={activeSection}
          currentContent={identityFoundation[activeSection as keyof typeof identityFoundation]}
          onApplySuggestion={(suggestion) => {
            setIdentityFoundation(prev => ({
              ...prev,
              [activeSection]: suggestion
            }));
            saveIdentityFoundation();
          }}
        />
      )}
      
      {/* Save Indicator */}
      {isSaving && (
        <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            <span>Saving...</span>
          </div>
        </div>
      )}
    </div>
  );
}
```

### 3. AI Assistance Modal
```typescript
// File: frontend/src/components/mountain/AIAssistanceModal.tsx

interface AIAssistanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  section: string;
  currentContent: string;
  onApplySuggestion: (suggestion: string) => void;
}

export function AIAssistanceModal({ 
  isOpen, 
  onClose, 
  section, 
  currentContent, 
  onApplySuggestion 
}: AIAssistanceModalProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [prompts, setPrompts] = useState<string[]>([]);
  const [examples, setExamples] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{role: 'user' | 'assistant', content: string}>>([]);
  const [userInput, setUserInput] = useState('');
  
  useEffect(() => {
    if (isOpen) {
      loadAIAssistance();
    }
  }, [isOpen, section]);
  
  const loadAIAssistance = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/basecamp/ai-assist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          section,
          current_content: currentContent
        })
      });
      
      const data = await response.json();
      setSuggestions(data.suggestions || []);
      setPrompts(data.prompts || []);
      setExamples(data.examples || []);
    } catch (error) {
      console.error('Failed to load AI assistance:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const sendChatMessage = async () => {
    if (!userInput.trim()) return;
    
    const newMessages = [...chatMessages, { role: 'user' as const, content: userInput }];
    setChatMessages(newMessages);
    setUserInput('');
    
    try {
      const response = await fetch('/api/v1/basecamp/ai-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          section,
          current_content: currentContent,
          messages: newMessages
        })
      });
      
      const data = await response.json();
      setChatMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
    } catch (error) {
      console.error('Failed to send chat message:', error);
    }
  };
  
  if (!isOpen) return null;
  
  const sectionTitles = {
    values: 'Core Values',
    energy_amplifiers: 'Energy Amplifiers',
    energy_drainers: 'Energy Drainers',
    personality_notes: 'Personality Notes'
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">
            AI Assistant: {sectionTitles[section as keyof typeof sectionTitles]}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex h-[70vh]">
          {/* Left Panel - Suggestions & Examples */}
          <div className="w-1/2 p-6 border-r overflow-y-auto">
            {isLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Quick Suggestions */}
                {suggestions.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Quick Suggestions</h3>
                    <div className="space-y-2">
                      {suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => onApplySuggestion(suggestion)}
                          className="w-full text-left p-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-sm transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Reflection Prompts */}
                {prompts.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Reflection Prompts</h3>
                    <div className="space-y-2">
                      {prompts.map((prompt, index) => (
                        <div key={index} className="p-3 bg-gray-50 rounded-lg text-sm text-gray-700">
                          {prompt}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Examples */}
                {examples.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-800 mb-3">Examples</h3>
                    <div className="space-y-2">
                      {examples.map((example, index) => (
                        <div key={index} className="p-3 bg-green-50 rounded-lg text-sm text-gray-700">
                          {example}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
          
          {/* Right Panel - AI Chat */}
          <div className="w-1/2 flex flex-col">
            <div className="p-4 border-b">
              <h3 className="font-medium text-gray-800">Chat with AI</h3>
              <p className="text-sm text-gray-600">Ask questions or get personalized guidance</p>
            </div>
            
            <div className="flex-1 p-4 overflow-y-auto">
              <div className="space-y-4">
                {chatMessages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-lg text-sm ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="p-4 border-t">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask about your values, strengths, or get guidance..."
                  className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={sendChatMessage}
                  disabled={!userInput.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

### 4. Journey Tab Component
```typescript
// File: frontend/src/components/mountain/JourneyTab.tsx

interface JourneyTabProps {
  userId: string;
}

export function JourneyTab({ userId }: JourneyTabProps) {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  
  useEffect(() => {
    loadEntries();
  }, [userId]);
  
  const loadEntries = async (pageNum = 1) => {
    try {
      const response = await fetch(`/api/v1/entries?user_id=${userId}&page=${pageNum}&limit=20`);
      const data = await response.json();
      
      if (pageNum === 1) {
        setEntries(data.entries);
      } else {
        setEntries(prev => [...prev, ...data.entries]);
      }
      
      setHasMore(data.pagination.page * data.pagination.limit < data.pagination.total);
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to load entries:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const loadMore = () => {
    if (hasMore && !isLoading) {
      loadEntries(page + 1);
    }
  };
  
  if (isLoading && entries.length === 0) {
    return <JourneySkeleton />;
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Your Journey</h1>
        <p className="text-gray-600">
          Track your progress through sessions and reflections over time.
        </p>
      </div>
      
      {entries.length === 0 ? (
        <div className="text-center py-12">
          <Map className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">Your journey starts here</h3>
          <p className="text-gray-500 mb-6">Add your first entry to begin tracking your progress.</p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
            Add Entry
          </button>
        </div>
      ) : (
        <TimelineComponent 
          entries={entries}
          onLoadMore={loadMore}
          hasMore={hasMore}
          isLoading={isLoading}
        />
      )}
    </div>
  );
}
```

### 5. Timeline Component
```typescript
// File: frontend/src/components/mountain/TimelineComponent.tsx

interface TimelineComponentProps {
  entries: Entry[];
  onLoadMore: () => void;
  hasMore: boolean;
  isLoading: boolean;
}

export function TimelineComponent({ entries, onLoadMore, hasMore, isLoading }: TimelineComponentProps) {
  const [selectedEntry, setSelectedEntry] = useState<Entry | null>(null);
  
  // Group entries by month
  const groupedEntries = entries.reduce((groups, entry) => {
    const date = new Date(entry.session_date);
    const monthKey = `${date.getFullYear()}-${date.getMonth()}`;
    
    if (!groups[monthKey]) {
      groups[monthKey] = {
        month: date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
        entries: []
      };
    }
    
    groups[monthKey].entries.push(entry);
    return groups;
  }, {} as Record<string, { month: string; entries: Entry[] }>);
  
  return (
    <div className="relative">
      {/* Timeline Line */}
      <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
      
      <div className="space-y-8">
        {Object.values(groupedEntries).map((group, groupIndex) => (
          <div key={groupIndex}>
            {/* Month Header */}
            <div className="relative flex items-center mb-6">
              <div className="absolute left-6 w-4 h-4 bg-blue-500 rounded-full border-4 border-white shadow-lg"></div>
              <div className="ml-16">
                <h3 className="text-lg font-semibold text-gray-800">{group.month}</h3>
              </div>
            </div>
            
            {/* Entries for this month */}
            <div className="space-y-4">
              {group.entries.map((entry, entryIndex) => (
                <div key={entry.id} className="relative">
                  <div className="absolute left-7 w-2 h-2 bg-gray-400 rounded-full"></div>
                  <div className="ml-16">
                    <EntryCard 
                      entry={entry}
                      onClick={() => setSelectedEntry(entry)}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      {/* Load More */}
      {hasMore && (
        <div className="text-center mt-8">
          <button
            onClick={onLoadMore}
            disabled={isLoading}
            className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-colors"
          >
            {isLoading ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}
      
      {/* Entry Details Modal */}
      {selectedEntry && (
        <EntryDetailsModal
          entry={selectedEntry}
          isOpen={!!selectedEntry}
          onClose={() => setSelectedEntry(null)}
        />
      )}
    </div>
  );
}
```

### 6. Destinations Tab Component
```typescript
// File: frontend/src/components/mountain/DestinationsTab.tsx

interface DestinationsTabProps {
  userId: string;
}

export function DestinationsTab({ userId }: DestinationsTabProps) {
  const [bigIdeas, setBigIdeas] = useState<Destination[]>([]);
  const [smallSteps, setSmallSteps] = useState<SmallStep[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    loadDestinationsData();
  }, [userId]);
  
  const loadDestinationsData = async () => {
    try {
      const [bigIdeasResponse, smallStepsResponse] = await Promise.all([
        fetch(`/api/v1/destinations/three-big-ideas?user_id=${userId}`),
        fetch(`/api/v1/small-steps?user_id=${userId}`)
      ]);
      
      const bigIdeasData = await bigIdeasResponse.json();
      const smallStepsData = await smallStepsResponse.json();
      
      setBigIdeas(bigIdeasData.big_ideas || []);
      setSmallSteps(smallStepsData.small_steps || []);
    } catch (error) {
      console.error('Failed to load destinations data:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  if (isLoading) {
    return <DestinationsSkeleton />;
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Your Destinations</h1>
        <p className="text-gray-600">
          Focus on your three big ideas and take small steps toward your goals.
        </p>
      </div>
      
      <div className="space-y-8">
        {/* Three Big Ideas */}
        <ThreeBigIdeas 
          bigIdeas={bigIdeas}
          onUpdate={loadDestinationsData}
          userId={userId}
        />
        
        {/* Small Steps */}
        <SmallStepsList 
          smallSteps={smallSteps}
          onUpdate={loadDestinationsData}
          userId={userId}
        />
      </div>
    </div>
  );
}
```

### 7. Three Big Ideas Component
```typescript
// File: frontend/src/components/mountain/ThreeBigIdeas.tsx

interface ThreeBigIdeasProps {
  bigIdeas: Destination[];
  onUpdate: () => void;
  userId: string;
}

export function ThreeBigIdeas({ bigIdeas, onUpdate, userId }: ThreeBigIdeasProps) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  
  const availableSlots = 3 - bigIdeas.length;
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Three Big Ideas</h2>
          <p className="text-sm text-gray-600">
            Your most important destinations - the big picture goals that drive you.
          </p>
        </div>
        
        {availableSlots > 0 && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Add Big Idea
          </button>
        )}
      </div>
      
      <div className="grid gap-6 md:grid-cols-3">
        {/* Existing Big Ideas */}
        {bigIdeas.map((idea, index) => (
          <BigIdeaCard 
            key={idea.id}
            idea={idea}
            rank={index + 1}
            onUpdate={onUpdate}
          />
        ))}
        
        {/* Empty Slots */}
        {Array.from({ length: availableSlots }).map((_, index) => (
          <div
            key={`empty-${index}`}
            onClick={() => setShowCreateModal(true)}
            className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors"
          >
            <Plus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-gray-500 font-medium">Add Big Idea #{bigIdeas.length + index + 1}</p>
          </div>
        ))}
      </div>
      
      {/* Create Modal */}
      {showCreateModal && (
        <CreateDestinationModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={onUpdate}
          userId={userId}
          isBigIdea={true}
        />
      )}
    </div>
  );
}
```

## Backend Implementation

### 1. Basecamp API Endpoints
```python
# File: backend/app/api/v1/basecamp.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.basecamp_service import BasecampService
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/basecamp")
async def get_identity_foundation(
    user_id: str,