from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from app.services.quote_service import QuoteService
from app.api.v1.deps import get_current_user_clerk_id
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class QuoteLikeRequest(BaseModel):
    liked: bool


class CreateQuoteRequest(BaseModel):
    quote_text: str
    author: str
    source: Optional[str] = None
    category: str
    tags: List[str] = []


@router.get("/quotes")
async def get_daily_quotes(
    count: int = 5,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
):
    """Get personalized daily quotes for carousel"""
    try:
        logger.info(f"=== GET /quotes called ===")
        logger.info(f"Getting {count} daily quotes for user: {user_info['clerk_user_id']}")
        
        quote_service = QuoteService()
        quotes = await quote_service.get_daily_quotes(user_info["clerk_user_id"], count)
        
        logger.info(f"✅ Successfully retrieved {len(quotes)} quotes")
        return {"quotes": quotes}
        
    except Exception as e:
        logger.error(f"❌ Error getting daily quotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get daily quotes"
        )


@router.post("/quotes/{quote_id}/like")
async def like_quote(
    quote_id: str,
    like_data: QuoteLikeRequest,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
):
    """Like or unlike a quote"""
    try:
        logger.info(f"=== POST /quotes/{quote_id}/like called ===")
        logger.info(f"User {user_info['clerk_user_id']} {'liking' if like_data.liked else 'unliking'} quote {quote_id}")
        
        quote_service = QuoteService()
        result = await quote_service.like_quote(user_info["clerk_user_id"], quote_id)
        
        logger.info(f"✅ Successfully processed like action")
        return result
        
    except ValueError as e:
        logger.error(f"❌ Quote not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    except Exception as e:
        logger.error(f"❌ Error liking quote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like quote"
        )


@router.get("/quotes/favorites")
async def get_favorite_quotes(
    limit: int = 20,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
):
    """Get user's favorite quotes"""
    try:
        logger.info(f"=== GET /quotes/favorites called ===")
        logger.info(f"Getting favorite quotes for user: {user_info['clerk_user_id']}")
        
        quote_service = QuoteService()
        favorites = await quote_service.get_user_favorites(user_info["clerk_user_id"], limit)
        
        logger.info(f"✅ Successfully retrieved {len(favorites)} favorite quotes")
        return {"favorite_quotes": favorites}
        
    except Exception as e:
        logger.error(f"❌ Error getting favorite quotes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get favorite quotes"
        )


@router.get("/quotes/category/{category}")
async def get_quotes_by_category(
    category: str,
    limit: int = 10,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
):
    """Get quotes by category"""
    try:
        logger.info(f"=== GET /quotes/category/{category} called ===")
        logger.info(f"Getting quotes for category: {category}")
        
        quote_service = QuoteService()
        quotes = await quote_service.get_quotes_by_category(category, user_info["clerk_user_id"], limit)
        
        logger.info(f"✅ Successfully retrieved {len(quotes)} quotes for category {category}")
        return {"quotes": quotes}
        
    except Exception as e:
        logger.error(f"❌ Error getting quotes by category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get quotes by category"
        )


# Admin endpoints (for future use)
@router.post("/admin/quotes")
async def create_quote(
    quote_data: CreateQuoteRequest,
    user_info: Dict[str, Any] = Depends(get_current_user_clerk_id)
):
    """Create a new quote (admin only)"""
    try:
        logger.info(f"=== POST /admin/quotes called ===")
        logger.info(f"Creating quote by user: {user_info['clerk_user_id']}")
        
        # TODO: Add admin role check
        # if user_info["primary_role"] != "admin":
        #     raise HTTPException(status_code=403, detail="Admin access required")
        
        quote_service = QuoteService()
        quote = await quote_service.create_quote(
            quote_data.model_dump(),
            user_info["clerk_user_id"]
        )
        
        logger.info(f"✅ Successfully created quote: {quote.id}")
        return {
            "id": str(quote.id),
            "quote_text": quote.quote_text,
            "author": quote.author,
            "source": quote.source,
            "category": quote.category,
            "tags": quote.tags
        }
        
    except Exception as e:
        logger.error(f"❌ Error creating quote: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create quote"
        )