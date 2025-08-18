"""Search endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from core.config import settings
from core.redis import rate_limiter
from search.pipeline import SearchPipeline

logger = logging.getLogger(__name__)

router = APIRouter()
search_pipeline = SearchPipeline()


class SearchRequest(BaseModel):
    """Search request model."""

    text: str = Field(..., min_length=3, max_length=1000, description="User's worry or query text")
    max_results: Optional[int] = Field(
        default=20, ge=1, le=100, description="Maximum number of results to return"
    )
    max_subreddits: Optional[int] = Field(
        default=None, ge=1, le=20, description="Maximum number of subreddits to search"
    )


class SearchResponse(BaseModel):
    """Search response model."""

    query: dict
    subreddits: list
    posts: list
    metadata: dict


@router.post("/ingest/search", response_model=SearchResponse)
async def search_posts(request: SearchRequest, http_request: Request):
    """
    Search for relevant Reddit posts based on user's worry/query.

    This endpoint:
    1. Extracts key phrases from the user's text
    2. Finds relevant subreddits using semantic similarity
    3. Searches for posts in those subreddits
    4. Ranks results using composite scoring
    5. Returns structured results with metadata
    """
    # Rate limiting
    client_ip = http_request.client.host
    if not await rate_limiter.is_allowed(
        key=f"search:{client_ip}",
        limit=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
        window_seconds=60,
    ):
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again later.",
        )

    try:
        logger.info(f"Processing search request: '{request.text[:50]}...'")

        # Execute search pipeline
        results = await search_pipeline.search(
            query_text=request.text,
            max_results=request.max_results,
            max_subreddits=request.max_subreddits,
        )

        return SearchResponse(**results)

    except Exception as e:
        logger.error(f"Search request failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Search request failed. Please try again.",
        ) from e


@router.get("/metrics")
async def get_search_metrics():
    """Get basic search metrics and statistics."""
    # TODO: Implement proper metrics collection
    return {
        "message": "Metrics endpoint - TODO: implement proper metrics collection",
        "placeholder_metrics": {
            "total_searches": 0,
            "average_response_time": 0.0,
            "popular_subreddits": [],
        },
    }
