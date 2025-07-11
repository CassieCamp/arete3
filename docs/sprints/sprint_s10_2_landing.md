# Sprint S10.2: Landing Page & Quote System

**Epic**: [Sprint S10 Application Redesign](./sprint_s10_redesign_epic.md)  
**Duration**: 1 week  
**Priority**: High  
**Dependencies**: Sprint S10.1 (Foundation & Database Migration)

## Sprint Overview

This sprint implements the new main landing page with quote carousel and bottom navigation, establishing the foundation for the redesigned user experience. It introduces the quote management system and creates the entry point for the unified entry system.

## Sprint Goals

1. **Implement quote carousel** with heart functionality and personalization
2. **Create bottom navigation** with Mountain/Microphone/Compass icons
3. **Build quote management system** with admin interface
4. **Add first-time user tooltips** and onboarding experience
5. **Establish responsive design** patterns for mobile-first approach

## Wireframe Reference

Based on wireframe analysis:
- **Main landing page** with quote carousel at top
- **Bottom navigation** with three primary icons
- **Heart functionality** for quote likes/favorites
- **Tooltip system** for first-time user guidance

## Frontend Components

### 1. Main Landing Page Component
```typescript
// File: frontend/src/app/dashboard/page.tsx (Updated)

interface MainLandingPageProps {
  user: User;
  freemiumStatus: FreemiumStatus;
}

export default function MainLandingPage({ user, freemiumStatus }: MainLandingPageProps) {
  const [showTooltips, setShowTooltips] = useState(!user.dashboard_preferences?.tooltips_shown);
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Quote Carousel Section */}
      <div className="pt-8 pb-6">
        <QuoteCarousel userId={user.id} />
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 px-4">
        {/* Entry Creation CTA */}
        <UnifiedEntryCTA 
          freemiumStatus={freemiumStatus}
          showTooltip={showTooltips}
          onTooltipDismiss={() => setShowTooltips(false)}
        />
      </div>
      
      {/* Bottom Navigation */}
      <BottomNavigation 
        activeTab="mountain"
        showTooltips={showTooltips}
        onTooltipComplete={() => markTooltipsComplete(user.id)}
      />
    </div>
  );
}
```

### 2. Quote Carousel Component
```typescript
// File: frontend/src/components/quotes/QuoteCarousel.tsx

interface Quote {
  id: string;
  quote_text: string;
  author: string;
  source?: string;
  user_liked: boolean;
}

interface QuoteCarouselProps {
  userId: string;
}

export function QuoteCarousel({ userId }: QuoteCarouselProps) {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    loadDailyQuotes();
  }, [userId]);
  
  const loadDailyQuotes = async () => {
    try {
      const response = await fetch(`/api/v1/quotes/daily?user_id=${userId}`);
      const data = await response.json();
      setQuotes(data.quotes);
    } catch (error) {
      console.error('Failed to load quotes:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleLikeQuote = async (quoteId: string) => {
    try {
      await fetch(`/api/v1/quotes/${quoteId}/like`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ liked: !quotes[currentIndex].user_liked })
      });
      
      // Update local state
      setQuotes(prev => prev.map(quote => 
        quote.id === quoteId 
          ? { ...quote, user_liked: !quote.user_liked }
          : quote
      ));
    } catch (error) {
      console.error('Failed to like quote:', error);
    }
  };
  
  const nextQuote = () => {
    setCurrentIndex((prev) => (prev + 1) % quotes.length);
  };
  
  const prevQuote = () => {
    setCurrentIndex((prev) => (prev - 1 + quotes.length) % quotes.length);
  };
  
  if (isLoading) {
    return <QuoteCarouselSkeleton />;
  }
  
  const currentQuote = quotes[currentIndex];
  
  return (
    <div className="relative px-6 py-8">
      <div className="max-w-md mx-auto">
        {/* Quote Content */}
        <div className="text-center mb-6">
          <blockquote className="text-lg font-medium text-gray-800 mb-4 leading-relaxed">
            "{currentQuote.quote_text}"
          </blockquote>
          <cite className="text-sm text-gray-600">
            — {currentQuote.author}
            {currentQuote.source && (
              <span className="block text-xs text-gray-500 mt-1">
                {currentQuote.source}
              </span>
            )}
          </cite>
        </div>
        
        {/* Heart Button */}
        <div className="flex justify-center mb-6">
          <button
            onClick={() => handleLikeQuote(currentQuote.id)}
            className={`p-3 rounded-full transition-all duration-200 ${
              currentQuote.user_liked
                ? 'bg-red-100 text-red-500 scale-110'
                : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
            }`}
          >
            <Heart 
              className={`w-6 h-6 ${currentQuote.user_liked ? 'fill-current' : ''}`} 
            />
          </button>
        </div>
        
        {/* Navigation Arrows */}
        <div className="flex justify-between items-center">
          <button
            onClick={prevQuote}
            className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* Dots Indicator */}
          <div className="flex space-x-2">
            {quotes.map((_, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
          
          <button
            onClick={nextQuote}
            className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
          >
            <ChevronRight className="w-5 h-5 text-gray-600" />
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 3. Bottom Navigation Component
```typescript
// File: frontend/src/components/navigation/BottomNavigation.tsx

interface BottomNavigationProps {
  activeTab: 'mountain' | 'microphone' | 'compass';
  showTooltips: boolean;
  onTooltipComplete: () => void;
}

export function BottomNavigation({ activeTab, showTooltips, onTooltipComplete }: BottomNavigationProps) {
  const [tooltipStep, setTooltipStep] = useState(0);
  const router = useRouter();
  
  const navigationItems = [
    {
      id: 'mountain',
      icon: Mountain,
      label: 'Mountain',
      description: 'Your journey, identity, and destinations',
      href: '/dashboard/mountain'
    },
    {
      id: 'microphone',
      icon: Mic,
      label: 'Entry',
      description: 'Add sessions and fresh thoughts',
      action: 'openEntryModal'
    },
    {
      id: 'compass',
      icon: Compass,
      label: 'Coach',
      description: 'Connect with your coach',
      href: '/dashboard/coach'
    }
  ];
  
  const handleNavigation = (item: typeof navigationItems[0]) => {
    if (item.action === 'openEntryModal') {
      // Open unified entry modal
      // This will be implemented in Sprint S10.3
      console.log('Opening entry modal...');
    } else if (item.href) {
      router.push(item.href);
    }
  };
  
  const nextTooltip = () => {
    if (tooltipStep < navigationItems.length - 1) {
      setTooltipStep(tooltipStep + 1);
    } else {
      onTooltipComplete();
    }
  };
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-2">
      <div className="flex justify-around items-center max-w-md mx-auto">
        {navigationItems.map((item, index) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          const showTooltip = showTooltips && tooltipStep === index;
          
          return (
            <div key={item.id} className="relative">
              {/* Tooltip */}
              {showTooltip && (
                <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gray-900 text-white text-xs rounded-lg px-3 py-2 whitespace-nowrap">
                    <div className="font-medium">{item.label}</div>
                    <div className="text-gray-300">{item.description}</div>
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2">
                      <div className="border-4 border-transparent border-t-gray-900"></div>
                    </div>
                  </div>
                  <button
                    onClick={nextTooltip}
                    className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white text-xs px-2 py-1 rounded"
                  >
                    {index < navigationItems.length - 1 ? 'Next' : 'Got it!'}
                  </button>
                </div>
              )}
              
              {/* Navigation Button */}
              <button
                onClick={() => handleNavigation(item)}
                className={`p-3 rounded-full transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-100 text-blue-600 scale-110'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-6 h-6" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### 4. Unified Entry CTA Component
```typescript
// File: frontend/src/components/entries/UnifiedEntryCTA.tsx

interface UnifiedEntryCTAProps {
  freemiumStatus: FreemiumStatus;
  showTooltip: boolean;
  onTooltipDismiss: () => void;
}

export function UnifiedEntryCTA({ freemiumStatus, showTooltip, onTooltipDismiss }: UnifiedEntryCTAProps) {
  const [showEntryModal, setShowEntryModal] = useState(false);
  
  const canCreateEntry = freemiumStatus.has_coach || freemiumStatus.entries_remaining > 0;
  
  return (
    <div className="relative">
      {/* Main CTA Button */}
      <button
        onClick={() => setShowEntryModal(true)}
        disabled={!canCreateEntry}
        className={`w-full p-6 rounded-xl border-2 border-dashed transition-all duration-200 ${
          canCreateEntry
            ? 'border-blue-300 bg-blue-50 hover:border-blue-400 hover:bg-blue-100'
            : 'border-gray-300 bg-gray-50 cursor-not-allowed'
        }`}
      >
        <div className="text-center">
          <Plus className={`w-8 h-8 mx-auto mb-2 ${
            canCreateEntry ? 'text-blue-500' : 'text-gray-400'
          }`} />
          <h3 className={`text-lg font-medium mb-1 ${
            canCreateEntry ? 'text-gray-800' : 'text-gray-500'
          }`}>
            Add Entry
          </h3>
          <p className={`text-sm ${
            canCreateEntry ? 'text-gray-600' : 'text-gray-400'
          }`}>
            Share a recent session or fresh thought
          </p>
          
          {/* Freemium Warning */}
          {!freemiumStatus.has_coach && (
            <div className="mt-3 text-xs text-orange-600">
              {freemiumStatus.entries_remaining} free entries remaining
            </div>
          )}
        </div>
      </button>
      
      {/* Tooltip for first-time users */}
      {showTooltip && (
        <div className="absolute -top-16 left-1/2 transform -translate-x-1/2">
          <div className="bg-gray-900 text-white text-sm rounded-lg px-4 py-2 whitespace-nowrap">
            Tap here to add your first entry!
            <button
              onClick={onTooltipDismiss}
              className="ml-2 text-blue-300 hover:text-blue-200"
            >
              ✕
            </button>
            <div className="absolute top-full left-1/2 transform -translate-x-1/2">
              <div className="border-4 border-transparent border-t-gray-900"></div>
            </div>
          </div>
        </div>
      )}
      
      {/* Entry Modal - Placeholder for Sprint S10.3 */}
      {showEntryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-semibold mb-4">Add Entry</h2>
            <p className="text-gray-600 mb-4">
              Entry creation will be implemented in Sprint S10.3
            </p>
            <button
              onClick={() => setShowEntryModal(false)}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Backend Implementation

### 1. Quote API Endpoints
```python
# File: backend/app/api/v1/quotes.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.quote_service import QuoteService
from app.services.auth_service import get_current_user

router = APIRouter()

@router.get("/quotes/daily")
async def get_daily_quotes(
    user_id: str,
    count: int = 5,
    current_user = Depends(get_current_user)
):
    """Get personalized daily quotes for carousel"""
    quote_service = QuoteService()
    quotes = await quote_service.get_daily_quotes(user_id, count)
    return {"quotes": quotes}

@router.post("/quotes/{quote_id}/like")
async def like_quote(
    quote_id: str,
    like_data: dict,
    current_user = Depends(get_current_user)
):
    """Like or unlike a quote"""
    quote_service = QuoteService()
    result = await quote_service.like_quote(current_user.id, quote_id, like_data["liked"])
    return {"success": True, "liked": result}

@router.get("/quotes/favorites")
async def get_favorite_quotes(
    current_user = Depends(get_current_user)
):
    """Get user's favorite quotes"""
    quote_service = QuoteService()
    favorites = await quote_service.get_user_favorites(current_user.id)
    return {"favorite_quotes": favorites}
```

### 2. Quote Service Implementation
```python
# File: backend/app/services/quote_service.py

from typing import List, Optional
from app.database import db
from datetime import datetime
import random

class QuoteService:
    def __init__(self):
        self.quotes_collection = db.quotes
        self.likes_collection = db.user_quote_likes
    
    async def get_daily_quotes(self, user_id: str, count: int = 5) -> List[dict]:
        """Get personalized daily quotes with favorites first"""
        # Get user's liked quotes
        liked_quotes = await self.likes_collection.find(
            {"user_id": user_id}
        ).to_list(length=None)
        liked_quote_ids = [like["quote_id"] for like in liked_quotes]
        
        # Get favorite quotes first
        favorite_quotes = []
        if liked_quote_ids:
            favorite_quotes = await self.quotes_collection.find(
                {"_id": {"$in": liked_quote_ids}, "active": True}
            ).to_list(length=min(count, len(liked_quote_ids)))
        
        # Fill remaining slots with random quotes
        remaining_count = count - len(favorite_quotes)
        if remaining_count > 0:
            other_quotes = await self.quotes_collection.find(
                {"_id": {"$nin": liked_quote_ids}, "active": True}
            ).to_list(length=None)
            
            # Randomly select remaining quotes
            if other_quotes:
                random.shuffle(other_quotes)
                other_quotes = other_quotes[:remaining_count]
            
            favorite_quotes.extend(other_quotes)
        
        # Format quotes with user_liked status
        formatted_quotes = []
        for quote in favorite_quotes:
            formatted_quotes.append({
                "id": str(quote["_id"]),
                "quote_text": quote["quote_text"],
                "author": quote["author"],
                "source": quote.get("source"),
                "user_liked": str(quote["_id"]) in liked_quote_ids
            })
        
        # Update display count
        quote_ids = [quote["_id"] for quote in favorite_quotes]
        await self.quotes_collection.update_many(
            {"_id": {"$in": quote_ids}},
            {"$inc": {"display_count": 1}}
        )
        
        return formatted_quotes
    
    async def like_quote(self, user_id: str, quote_id: str, liked: bool) -> bool:
        """Like or unlike a quote"""
        if liked:
            # Add like
            await self.likes_collection.update_one(
                {"user_id": user_id, "quote_id": quote_id},
                {"$set": {"liked_at": datetime.utcnow()}},
                upsert=True
            )
            # Increment like count
            await self.quotes_collection.update_one(
                {"_id": quote_id},
                {"$inc": {"like_count": 1}}
            )
        else:
            # Remove like
            result = await self.likes_collection.delete_one(
                {"user_id": user_id, "quote_id": quote_id}
            )
            if result.deleted_count > 0:
                # Decrement like count
                await self.quotes_collection.update_one(
                    {"_id": quote_id},
                    {"$inc": {"like_count": -1}}
                )
        
        return liked
    
    async def get_user_favorites(self, user_id: str) -> List[dict]:
        """Get user's favorite quotes"""
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$lookup": {
                "from": "quotes",
                "localField": "quote_id",
                "foreignField": "_id",
                "as": "quote"
            }},
            {"$unwind": "$quote"},
            {"$project": {
                "id": {"$toString": "$quote._id"},
                "quote_text": "$quote.quote_text",
                "author": "$quote.author",
                "liked_at": "$liked_at"
            }},
            {"$sort": {"liked_at": -1}}
        ]
        
        favorites = await self.likes_collection.aggregate(pipeline).to_list(length=None)
        return favorites
```

### 3. Initial Quote Data
```python
# File: backend/app/data/initial_quotes.py

INITIAL_QUOTES = [
    {
        "quote_text": "The cave you fear to enter holds the treasure you seek.",
        "author": "Joseph Campbell",
        "source": "The Hero with a Thousand Faces",
        "category": "courage",
        "tags": ["growth", "fear", "courage"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
        "author": "Ralph Waldo Emerson",
        "category": "motivation",
        "tags": ["inner-strength", "potential", "self-belief"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "The only way to do great work is to love what you do.",
        "author": "Steve Jobs",
        "category": "motivation",
        "tags": ["passion", "work", "excellence"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "Leadership is not about being in charge. It's about taking care of those in your charge.",
        "author": "Simon Sinek",
        "category": "leadership",
        "tags": ["leadership", "service", "responsibility"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "The greatest glory in living lies not in never falling, but in rising every time we fall.",
        "author": "Nelson Mandela",
        "category": "growth",
        "tags": ["resilience", "perseverance", "growth"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    }
]

async def seed_initial_quotes():
    """Seed database with initial quotes"""
    from app.database import db
    
    for quote_data in INITIAL_QUOTES:
        quote_data["created_at"] = datetime.utcnow()
        quote_data["updated_at"] = datetime.utcnow()
        
        await db.quotes.update_one(
            {"quote_text": quote_data["quote_text"], "author": quote_data["author"]},
            {"$set": quote_data},
            upsert=True
        )
```

## Admin Interface (Simple)

### 1. Quote Management Component
```typescript
// File: frontend/src/app/admin/quotes/page.tsx

export default function QuoteManagement() {
  const [quotes, setQuotes] = useState([]);
  const [newQuote, setNewQuote] = useState({
    quote_text: '',
    author: '',
    source: '',
    category: 'motivation'
  });
  
  const addQuote = async () => {
    try {
      await fetch('/api/v1/admin/quotes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newQuote)
      });
      
      setNewQuote({ quote_text: '', author: '', source: '', category: 'motivation' });
      loadQuotes();
    } catch (error) {
      console.error('Failed to add quote:', error);
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">Quote Management</h1>
      
      {/* Add Quote Form */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Add New Quote</h2>
        <div className="space-y-4">
          <textarea
            placeholder="Quote text..."
            value={newQuote.quote_text}
            onChange={(e) => setNewQuote({...newQuote, quote_text: e.target.value})}
            className="w-full p-3 border rounded-lg"
            rows={3}
          />
          <input
            placeholder="Author"
            value={newQuote.author}
            onChange={(e) => setNewQuote({...newQuote, author: e.target.value})}
            className="w-full p-3 border rounded-lg"
          />
          <input
            placeholder="Source (optional)"
            value={newQuote.source}
            onChange={(e) => setNewQuote({...newQuote, source: e.target.value})}
            className="w-full p-3 border rounded-lg"
          />
          <select
            value={newQuote.category}
            onChange={(e) => setNewQuote({...newQuote, category: e.target.value})}
            className="w-full p-3 border rounded-lg"
          >
            <option value="motivation">Motivation</option>
            <option value="leadership">Leadership</option>
            <option value="growth">Growth</option>
            <option value="courage">Courage</option>
          </select>
          <button
            onClick={addQuote}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
          >
            Add Quote
          </button>
        </div>
      </div>
      
      {/* Quotes List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Existing Quotes</h2>
          <div className="space-y-4">
            {quotes.map((quote) => (
              <div key={quote.id} className="border rounded-lg p-4">
                <blockquote className="text-gray-800 mb-2">
                  "{quote.quote_text}"
                </blockquote>
                <cite className="text-sm text-gray-600">
                  — {quote.author}
                  {quote.source && ` (${quote.source})`}
                </cite>
                <div className="mt-2 text-xs text-gray-500">
                  Displayed: {quote.display_count} times | Liked: {quote.like_count} times
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

## Testing Strategy

### 1. Component Testing
- [ ] **Quote Carousel**: Swipe functionality, heart interactions, navigation
- [ ] **Bottom Navigation**: Tooltip sequence, navigation actions
- [ ] **Responsive Design**: Mobile and desktop layouts

### 2. API Testing
- [ ] **Quote Endpoints**: CRUD operations, personalization logic
- [ ] **Like System**: Toggle functionality, count updates
- [ ] **Performance**: Quote loading and caching

### 3. User Experience Testing
- [ ] **First-Time User Flow**: Tooltip sequence completion
- [ ] **Quote Personalization**: Favorites appearing first
- [ ] **Accessibility**: Screen reader support, keyboard navigation

## Deployment Plan

### Day 1-2: Backend Implementation
- [ ] Implement quote service and API endpoints
- [ ] Seed initial quote data
- [ ] Create admin interface for quote management

### Day 3-4: Frontend Implementation
- [ ] Build quote carousel component
- [ ] Implement bottom navigation with tooltips
- [ ] Create main landing page layout

### Day 5: Integration & Testing
- [ ] Integration testing between frontend and backend
- [ ] User experience testing and refinements
- [ ] Performance optimization and deployment

## Success Criteria

### Technical Success
- [ ] Quote carousel functional with smooth navigation
- [ ] Heart functionality working with backend persistence
- [ ] Bottom navigation with working tooltip system
- [ ] Responsive design working on mobile and desktop

### User Experience Success
- [ ] Intuitive quote interaction (swipe, heart, navigate)
- [ ] Clear first-time user guidance through tooltips
- [ ] Smooth transitions and animations
- [ ] Accessible interface for all users

### Business Success
- [ ] Quote engagement metrics tracking
- [ ] User preference data collection
- [ ] Foundation for entry creation flow
- [ ] Positive user feedback on new landing experience

## Dependencies for Next Sprint

This sprint prepares the foundation for Sprint S10.3 (Unified Entry System):
- [ ] **Entry CTA Component**: Placeholder ready for modal integration
- [ ] **Navigation System**: Microphone button ready for entry modal trigger
- [ ] **User Preferences**: Tooltip completion tracking established
- [ ] **Responsive Framework**: Design patterns established for entry forms

---

**Sprint S10.2 establishes the new user experience foundation with quote system and navigation, setting the stage for the unified entry system in the next sprint.**