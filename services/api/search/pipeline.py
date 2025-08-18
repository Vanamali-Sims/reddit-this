"""
Main search pipeline orchestrating all components.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional

import numpy as np
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_db
from models.post import Post
from models.subreddit import Subreddit
from nlp.embeddings import embed_single_text, embed_texts
from nlp.expand import QueryExpander
from nlp.extract import TextExtractor
from reddit.client import reddit_client
from search.rank import PostRanker

logger = logging.getLogger(__name__)


class SearchPipeline:
    """Main search pipeline for Reddit worry finder."""

    def __init__(self):
        self.text_extractor = TextExtractor()
        self.query_expander = QueryExpander()
        self.post_ranker = PostRanker()

    async def search(
        self,
        query_text: str,
        max_results: int = 20,
        max_subreddits: int = None,
    ) -> Dict:
        """
        Execute complete search pipeline.

        Args:
            query_text: User's worry/query text
            max_results: Maximum number of results to return
            max_subreddits: Maximum number of subreddits to search

        Returns:
            Dictionary with subreddits, posts, and metadata
        """
        start_time = time.time()
        max_subreddits = max_subreddits or settings.MAX_SUBREDDITS_TO_SEARCH

        logger.info(f"Starting search pipeline for query: '{query_text[:50]}...'")

        try:
            # Step 1: Extract and expand query
            extraction_result = self.text_extractor.process_query(query_text)
            expanded_terms = self.query_expander.expand_query_terms(
                extraction_result["keyphrases"]
            )

            # Step 2: Generate query embedding
            query_embedding = await embed_single_text(query_text)

            # Step 3: Find relevant subreddits
            relevant_subreddits = await self._find_relevant_subreddits(
                query_embedding, extraction_result["search_terms"], max_subreddits
            )

            # Step 4: Search posts in relevant subreddits
            all_posts = await self._search_posts_in_subreddits(
                relevant_subreddits, extraction_result["search_terms"]
            )

            # Step 5: Embed and rank posts
            ranked_posts = await self._embed_and_rank_posts(
                all_posts, query_embedding, relevant_subreddits
            )

            # Step 6: Store results in database
            await self._store_results(relevant_subreddits, ranked_posts)

            end_time = time.time()
            processing_time = end_time - start_time

            logger.info(
                f"Search completed in {processing_time:.2f}s. "
                f"Found {len(ranked_posts)} posts across {len(relevant_subreddits)} subreddits."
            )

            return {
                "query": {
                    "original_text": query_text,
                    "normalized_text": extraction_result["normalized_text"],
                    "keyphrases": extraction_result["keyphrases"],
                    "search_terms": extraction_result["search_terms"],
                    "expanded_terms": expanded_terms,
                },
                "subreddits": [
                    {
                        "name": sub["name"],
                        "title": sub["title"],
                        "relevance_score": sub["relevance_score"],
                        "quality_score": sub["quality_score"],
                    }
                    for sub in relevant_subreddits
                ],
                "posts": ranked_posts[:max_results],
                "metadata": {
                    "total_posts_found": len(ranked_posts),
                    "subreddits_searched": len(relevant_subreddits),
                    "processing_time_seconds": processing_time,
                    "search_terms_used": len(extraction_result["search_terms"]),
                },
            }

        except Exception as e:
            logger.error(f"Search pipeline failed: {e}", exc_info=True)
            raise

    async def _find_relevant_subreddits(
        self, query_embedding: np.ndarray, search_terms: List[str], max_count: int
    ) -> List[Dict]:
        """Find and rank relevant subreddits."""
        # Get candidate subreddits from curated list
        candidate_subreddits = self._get_candidate_subreddits(search_terms)

        async with AsyncSession(bind=await get_db().__anext__()) as db:
            relevant_subreddits = []

            for subreddit_name in candidate_subreddits[:max_count * 2]:  # Search more, filter later
                # Check if subreddit exists in DB
                result = await db.execute(
                    select(Subreddit).where(Subreddit.name == subreddit_name)
                )
                subreddit = result.scalar_one_or_none()

                if not subreddit:
                    # Fetch from Reddit and create
                    subreddit_info = await reddit_client.get_subreddit_info(subreddit_name)
                    if subreddit_info:
                        subreddit = await self._create_subreddit_record(db, subreddit_info)

                if subreddit:
                    # Calculate relevance if we have embedding
                    if subreddit.embedding and len(query_embedding) > 0:
                        similarity = await self._cosine_similarity(
                            query_embedding, np.array(subreddit.embedding)
                        )
                    else:
                        similarity = 0.5  # Default relevance

                    relevant_subreddits.append(
                        {
                            "name": subreddit.name,
                            "title": subreddit.title,
                            "about": subreddit.about,
                            "relevance_score": similarity,
                            "quality_score": subreddit.quality_score,
                        }
                    )

            await db.commit()

        # Sort by relevance and return top results
        relevant_subreddits.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_subreddits[:max_count]

    async def _create_subreddit_record(self, db: AsyncSession, subreddit_info: Dict) -> Subreddit:
        """Create and embed subreddit record."""
        # Create embedding for subreddit
        description_text = f"{subreddit_info['title']} {subreddit_info['description']}"
        embedding = await embed_single_text(description_text)

        # Calculate quality score based on subscribers and other factors
        subscribers = subreddit_info.get("subscribers", 0)
        quality_score = min(np.log10(max(subscribers, 1)) / 6, 1.0)  # Log scale, max at 1M

        subreddit = Subreddit(
            name=subreddit_info["name"],
            title=subreddit_info["title"],
            about=subreddit_info["description"],
            embedding=embedding.tolist() if len(embedding) > 0 else None,
            quality_score=quality_score,
        )

        db.add(subreddit)
        return subreddit

    async def _search_posts_in_subreddits(
        self, subreddits: List[Dict], search_terms: List[str]
    ) -> List[Dict]:
        """Search for posts in relevant subreddits."""
        all_posts = []

        # Create search queries
        search_queries = search_terms[:5]  # Limit number of queries

        # Search each subreddit
        for subreddit in subreddits:
            subreddit_name = subreddit["name"]

            for query in search_queries:
                posts = await reddit_client.search_subreddit(
                    subreddit_name=subreddit_name,
                    query=query,
                    limit=settings.MAX_POSTS_PER_SUBREDDIT // len(search_queries),
                    time_filter="year",
                )

                # Add subreddit metadata to posts
                for post in posts:
                    post["subreddit_relevance"] = subreddit["relevance_score"]
                    post["subreddit_quality"] = subreddit["quality_score"]

                all_posts.extend(posts)

                # Rate limiting
                await asyncio.sleep(0.1)

        # Remove duplicates
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post["id"] not in seen_ids:
                seen_ids.add(post["id"])
                unique_posts.append(post)

        logger.info(f"Found {len(unique_posts)} unique posts across {len(subreddits)} subreddits")
        return unique_posts

    async def _embed_and_rank_posts(
        self, posts: List[Dict], query_embedding: np.ndarray, subreddits: List[Dict]
    ) -> List[Dict]:
        """Embed posts and rank using composite scoring."""
        if not posts:
            return []

        # Prepare text for embedding
        post_texts = []
        for post in posts:
            # Combine title and selftext for embedding
            text = f"{post['title']} {post.get('selftext', '')}"
            post_texts.append(text.strip())

        # Generate embeddings for all posts
        embeddings = await embed_texts(post_texts)

        # Add embeddings to posts
        for i, post in enumerate(posts):
            if i < len(embeddings):
                post["embedding"] = embeddings[i]

        # Create subreddit quality lookup
        subreddit_qualities = {sub["name"]: sub["quality_score"] for sub in subreddits}

        # Update subreddit stats for normalization
        subreddit_posts = {}
        for post in posts:
            subreddit_name = post["subreddit"]
            if subreddit_name not in subreddit_posts:
                subreddit_posts[subreddit_name] = []
            subreddit_posts[subreddit_name].append(post)

        for subreddit_name, sub_posts in subreddit_posts.items():
            self.post_ranker.update_subreddit_stats(subreddit_name, sub_posts)

        # Rank posts
        ranked_posts = self.post_ranker.rank_posts(
            posts, query_embedding, subreddit_qualities
        )

        return ranked_posts

    async def _store_results(self, subreddits: List[Dict], posts: List[Dict]) -> None:
        """Store search results in database."""
        async with AsyncSession(bind=await get_db().__anext__()) as db:
            # Store posts
            for post in posts:
                # Check if post already exists
                result = await db.execute(select(Post).where(Post.id == post["id"]))
                existing_post = result.scalar_one_or_none()

                if not existing_post:
                    # Create new post record
                    post_record = Post(
                        id=post["id"],
                        subreddit=post["subreddit"],
                        title=post["title"],
                        selftext=post.get("selftext", ""),
                        author=post.get("author"),
                        score=post.get("score", 0),
                        num_comments=post.get("num_comments", 0),
                        url=post.get("url"),
                        created_utc=post.get("created_utc"),
                        embedding=post.get("embedding", np.array([])).tolist()
                        if "embedding" in post and len(post["embedding"]) > 0
                        else None,
                    )
                    db.add(post_record)

            await db.commit()

    def _get_candidate_subreddits(self, search_terms: List[str]) -> List[str]:
        """Get candidate subreddits based on search terms."""
        # Base curated list of relevant subreddits
        base_subreddits = [
            "Hair",
            "HaircareScience",
            "FemaleHairLoss",
            "MaleHairLoss",
            "SebDerm",
            "SkincareAddiction",
            "Dermatology",
            "eczema",
            "AskDocs",
            "HealthAnxiety",
            "HairProducts",
            "NoPoo",
        ]

        # Add Australian-specific subreddits if context suggests Australia
        search_text_lower = " ".join(search_terms).lower()
        if any(term in search_text_lower for term in ["australia", "aussie", "au"]):
            base_subreddits.extend(["australia", "AskAnAustralian", "AusSkincare"])

        return base_subreddits

    async def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) == 0 or len(b) == 0:
            return 0.0

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))
