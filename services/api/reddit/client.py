"""
Reddit API client using asyncpraw.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional

import asyncpraw
from asyncpraw.models import Subreddit as PrawSubreddit
from asyncpraw.models import Submission

from core.config import settings

logger = logging.getLogger(__name__)


class RedditClient:
    """Async Reddit API client."""

    def __init__(self):
        self._reddit: Optional[asyncpraw.Reddit] = None

    async def _get_reddit(self) -> asyncpraw.Reddit:
        """Get or create Reddit instance."""
        if self._reddit is None:
            self._reddit = asyncpraw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT,
            )
        return self._reddit

    async def get_subreddit_info(self, subreddit_name: str) -> Optional[dict]:
        """
        Get subreddit metadata.

        Args:
            subreddit_name: Name of the subreddit

        Returns:
            Dictionary with subreddit info or None if not found
        """
        if settings.USE_REDDIT_MOCK:
            return self._mock_subreddit_info(subreddit_name)

        try:
            reddit = await self._get_reddit()
            subreddit: PrawSubreddit = await reddit.subreddit(subreddit_name)

            # Fetch basic info
            await subreddit.load()

            return {
                "name": subreddit.display_name,
                "title": subreddit.title,
                "description": getattr(subreddit, "public_description", ""),
                "subscribers": getattr(subreddit, "subscribers", 0),
                "created_utc": getattr(subreddit, "created_utc", None),
                "over18": getattr(subreddit, "over18", False),
            }

        except Exception as e:
            logger.warning(f"Failed to get subreddit info for {subreddit_name}: {e}")
            return None

    async def search_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 25,
        time_filter: str = "year",
        sort: str = "relevance",
    ) -> List[dict]:
        """
        Search posts in a specific subreddit.

        Args:
            subreddit_name: Name of the subreddit
            query: Search query
            limit: Maximum number of posts to return
            time_filter: Time filter (hour, day, week, month, year, all)
            sort: Sort method (relevance, hot, top, new, comments)

        Returns:
            List of post dictionaries
        """
        if settings.USE_REDDIT_MOCK:
            return self._mock_search_results(subreddit_name, query, limit)

        try:
            reddit = await self._get_reddit()
            subreddit: PrawSubreddit = await reddit.subreddit(subreddit_name)

            posts = []
            submission: Submission
            async for submission in subreddit.search(
                query, limit=limit, time_filter=time_filter, sort=sort
            ):
                post_data = await self._submission_to_dict(submission)
                posts.append(post_data)

            return posts

        except Exception as e:
            logger.warning(f"Failed to search {subreddit_name} for '{query}': {e}")
            return []

    async def _submission_to_dict(self, submission: Submission) -> dict:
        """Convert Reddit submission to dictionary."""
        return {
            "id": submission.id,
            "title": submission.title,
            "selftext": getattr(submission, "selftext", ""),
            "author": str(submission.author) if submission.author else "[deleted]",
            "score": submission.score,
            "num_comments": submission.num_comments,
            "url": submission.url,
            "permalink": f"https://reddit.com{submission.permalink}",
            "created_utc": datetime.fromtimestamp(
                submission.created_utc, tz=timezone.utc
            ),
            "subreddit": submission.subreddit.display_name,
            "upvote_ratio": getattr(submission, "upvote_ratio", 0.5),
            "is_self": submission.is_self,
        }

    def _mock_subreddit_info(self, subreddit_name: str) -> dict:
        """Mock subreddit info for development."""
        mock_data = {
            "Hair": {
                "name": "Hair",
                "title": "Hair care, styles, and health",
                "description": "Everything related to hair care, styling, and health issues",
                "subscribers": 150000,
                "created_utc": 1234567890,
                "over18": False,
            },
            "HaircareScience": {
                "name": "HaircareScience",
                "title": "Evidence-based hair care",
                "description": "Scientific approach to hair care and scalp health",
                "subscribers": 75000,
                "created_utc": 1234567890,
                "over18": False,
            },
            "SebDerm": {
                "name": "SebDerm",
                "title": "Seborrheic dermatitis support",
                "description": "Community for those dealing with seborrheic dermatitis",
                "subscribers": 25000,
                "created_utc": 1234567890,
                "over18": False,
            },
        }

        return mock_data.get(
            subreddit_name,
            {
                "name": subreddit_name,
                "title": f"{subreddit_name} community",
                "description": f"Discussion about {subreddit_name}",
                "subscribers": 10000,
                "created_utc": 1234567890,
                "over18": False,
            },
        )

    def _mock_search_results(
        self, subreddit_name: str, query: str, limit: int
    ) -> List[dict]:
        """Mock search results for development."""
        import hashlib
        import random

        # Create deterministic but varied results based on query hash
        query_hash = hashlib.md5(f"{subreddit_name}:{query}".encode()).hexdigest()
        random.seed(int(query_hash[:8], 16))

        posts = []
        for i in range(min(limit, random.randint(5, 15))):
            post_id = f"mock_{query_hash[:6]}_{i}"
            posts.append(
                {
                    "id": post_id,
                    "title": f"Mock post about {query} in {subreddit_name} #{i+1}",
                    "selftext": f"This is a mock post discussing {query}. "
                    f"It contains relevant information about the topic. "
                    f"This would normally be real Reddit content.",
                    "author": f"mock_user_{i}",
                    "score": random.randint(1, 100),
                    "num_comments": random.randint(0, 50),
                    "url": f"https://reddit.com/r/{subreddit_name}/comments/{post_id}/",
                    "permalink": f"/r/{subreddit_name}/comments/{post_id}/",
                    "created_utc": datetime.now(tz=timezone.utc),
                    "subreddit": subreddit_name,
                    "upvote_ratio": random.uniform(0.6, 0.95),
                    "is_self": True,
                }
            )

        return posts

    async def close(self):
        """Close the Reddit client."""
        if self._reddit:
            await self._reddit.close()


# Global client instance
reddit_client = RedditClient()
