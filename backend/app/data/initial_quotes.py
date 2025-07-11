from datetime import datetime
from typing import List, Dict, Any

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
    },
    {
        "quote_text": "Be yourself; everyone else is already taken.",
        "author": "Oscar Wilde",
        "category": "motivation",
        "tags": ["authenticity", "self-acceptance", "individuality"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "In the middle of difficulty lies opportunity.",
        "author": "Albert Einstein",
        "category": "growth",
        "tags": ["opportunity", "challenges", "perspective"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "The best time to plant a tree was 20 years ago. The second best time is now.",
        "author": "Chinese Proverb",
        "category": "motivation",
        "tags": ["action", "timing", "growth"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "Your limitation—it's only your imagination.",
        "author": "Unknown",
        "category": "motivation",
        "tags": ["limitations", "imagination", "potential"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "Great things never come from comfort zones.",
        "author": "Unknown",
        "category": "courage",
        "tags": ["comfort-zone", "growth", "challenge"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    },
    {
        "quote_text": "Luke Skywalker: What's in the cave?\nYoda: Only what you bring with you.",
        "author": "",
        "source": "The Empire Strikes Back",
        "category": "wisdom",
        "tags": ["wisdom", "self-reflection", "inner-journey", "fear"],
        "active": True,
        "display_count": 0,
        "like_count": 0,
        "created_by": "system"
    }
]


async def seed_initial_quotes():
    """Seed database with initial quotes"""
    from app.db.mongodb import get_database
    
    db = get_database()
    
    for quote_data in INITIAL_QUOTES:
        quote_data["created_at"] = datetime.utcnow()
        quote_data["updated_at"] = datetime.utcnow()
        
        # Use upsert to avoid duplicates
        await db.quotes.update_one(
            {"quote_text": quote_data["quote_text"], "author": quote_data["author"]},
            {"$set": quote_data},
            upsert=True
        )
    
    print(f"✅ Seeded {len(INITIAL_QUOTES)} initial quotes")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_initial_quotes())