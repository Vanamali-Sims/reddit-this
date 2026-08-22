"""
Main search pipeline orchestrating all components.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from core.config import settings
from nlp.embeddings import embed_single_text, embed_texts
from nlp.expand import QueryExpander
from nlp.extract import TextExtractor
from reddit.client import reddit_client
from search.rank import PostRanker

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


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
        """Execute complete search pipeline."""
        start_time = time.time()
        max_subreddits = max_subreddits or settings.MAX_SUBREDDITS_TO_SEARCH
        if settings.USE_DB_MOCK:
            max_subreddits = min(max_subreddits, 3)

        logger.info(f"Starting search pipeline for query: '{query_text[:50]}...'")

        try:
            extraction_result = self.text_extractor.process_query(query_text)
            if not extraction_result["search_terms"]:
                extraction_result["search_terms"] = [query_text.strip()]

            expanded_terms = self.query_expander.expand_query_terms(
                extraction_result["keyphrases"] or extraction_result["search_terms"]
            )

            query_embedding = await embed_single_text(query_text)

            relevant_subreddits = await self._find_relevant_subreddits(
                query_embedding, extraction_result["search_terms"], max_subreddits
            )

            all_posts = await self._search_posts_in_subreddits(
                relevant_subreddits, extraction_result["search_terms"]
            )

            ranked_posts = await self._embed_and_rank_posts(
                all_posts, query_embedding, relevant_subreddits
            )

            if not settings.USE_DB_MOCK:
                await self._store_results(relevant_subreddits, ranked_posts)

            processing_time = time.time() - start_time
            public_posts = self._public_posts(ranked_posts[:max_results])

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
                        "relevance_score": _to_float(sub["relevance_score"]),
                        "quality_score": _to_float(sub["quality_score"]),
                    }
                    for sub in relevant_subreddits
                ],
                "posts": public_posts,
                "metadata": {
                    "total_posts_found": len(ranked_posts),
                    "subreddits_searched": len(relevant_subreddits),
                    "processing_time_seconds": round(processing_time, 3),
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
        candidate_subreddits = self._get_candidate_subreddits(search_terms)[: max_count * 2]

        if settings.USE_DB_MOCK:
            return await self._find_subreddits_without_db(
                query_embedding, candidate_subreddits, max_count
            )

        return await self._find_subreddits_from_db(
            query_embedding, candidate_subreddits, max_count
        )

    async def _find_subreddits_without_db(
        self, query_embedding: np.ndarray, candidate_subreddits: List[str], max_count: int
    ) -> List[Dict]:
        """Build subreddit candidates from the Reddit client (mock or live) with no Postgres."""
        relevant_subreddits = []

        for subreddit_name in candidate_subreddits:
            subreddit_info = await reddit_client.get_subreddit_info(subreddit_name)
            if not subreddit_info:
                continue

            description_text = (
                f"{subreddit_info.get('title', '')} {subreddit_info.get('description', '')}"
            )
            embedding = await embed_single_text(description_text)
            if len(query_embedding) > 0 and len(embedding) > 0:
                similarity = await self._cosine_similarity(query_embedding, embedding)
            else:
                similarity = 0.5

            subscribers = subreddit_info.get("subscribers", 0)
            quality_score = min(np.log10(max(subscribers, 1)) / 6, 1.0)

            relevant_subreddits.append(
                {
                    "name": subreddit_info["name"],
                    "title": subreddit_info["title"],
                    "about": subreddit_info.get("description", ""),
                    "relevance_score": similarity,
                    "quality_score": quality_score,
                }
            )

        relevant_subreddits.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_subreddits[:max_count]

    async def _find_subreddits_from_db(
        self, query_embedding: np.ndarray, candidate_subreddits: List[str], max_count: int
    ) -> List[Dict]:
        """Look up subreddits in Postgres, creating records when missing."""
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession

        from core.db import get_db
        from models.subreddit import Subreddit

        async with AsyncSession(bind=await get_db().__anext__()) as db:
            relevant_subreddits = []

            for subreddit_name in candidate_subreddits:
                result = await db.execute(
                    select(Subreddit).where(Subreddit.name == subreddit_name)
                )
                subreddit = result.scalar_one_or_none()

                if not subreddit:
                    subreddit_info = await reddit_client.get_subreddit_info(subreddit_name)
                    if subreddit_info:
                        subreddit = await self._create_subreddit_record(db, subreddit_info)

                if subreddit:
                    if subreddit.embedding and len(query_embedding) > 0:
                        similarity = await self._cosine_similarity(
                            query_embedding, np.array(subreddit.embedding)
                        )
                    else:
                        similarity = 0.5

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

        relevant_subreddits.sort(key=lambda x: x["relevance_score"], reverse=True)
        return relevant_subreddits[:max_count]

    async def _create_subreddit_record(self, db, subreddit_info: Dict):
        """Create and embed subreddit record."""
        from models.subreddit import Subreddit

        description_text = f"{subreddit_info['title']} {subreddit_info['description']}"
        embedding = await embed_single_text(description_text)

        subscribers = subreddit_info.get("subscribers", 0)
        quality_score = min(np.log10(max(subscribers, 1)) / 6, 1.0)

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
        term_limit = 2 if settings.USE_DB_MOCK else 5
        search_queries = [term for term in search_terms[:term_limit] if term]
        if not search_queries:
            search_queries = ["advice"]

        per_query_limit = max(1, settings.MAX_POSTS_PER_SUBREDDIT // len(search_queries))
        if settings.USE_DB_MOCK:
            per_query_limit = min(per_query_limit, 8)

        for subreddit in subreddits:
            subreddit_name = subreddit["name"]

            for query in search_queries:
                posts = await reddit_client.search_subreddit(
                    subreddit_name=subreddit_name,
                    query=query,
                    limit=per_query_limit,
                    time_filter="year",
                )

                for post in posts:
                    post["subreddit_relevance"] = subreddit["relevance_score"]
                    post["subreddit_quality"] = subreddit["quality_score"]

                all_posts.extend(posts)

                if not settings.USE_DB_MOCK:
                    await asyncio.sleep(0.1)

        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post["id"] not in seen_ids:
                seen_ids.add(post["id"])
                unique_posts.append(post)

        logger.info(
            f"Found {len(unique_posts)} unique posts across {len(subreddits)} subreddits"
        )
        return unique_posts

    async def _embed_and_rank_posts(
        self, posts: List[Dict], query_embedding: np.ndarray, subreddits: List[Dict]
    ) -> List[Dict]:
        """Embed posts and rank using composite scoring."""
        if not posts:
            return []

        post_texts = []
        for post in posts:
            text = f"{post['title']} {post.get('selftext', '')}"
            post_texts.append(text.strip())

        embeddings = await embed_texts(post_texts)

        for i, post in enumerate(posts):
            if i < len(embeddings):
                post["embedding"] = embeddings[i]

        subreddit_qualities = {sub["name"]: sub["quality_score"] for sub in subreddits}

        subreddit_posts: Dict[str, List[Dict]] = {}
        for post in posts:
            subreddit_name = post["subreddit"]
            subreddit_posts.setdefault(subreddit_name, []).append(post)

        for subreddit_name, sub_posts in subreddit_posts.items():
            self.post_ranker.update_subreddit_stats(subreddit_name, sub_posts)

        return self.post_ranker.rank_posts(posts, query_embedding, subreddit_qualities)

    async def _store_results(self, subreddits: List[Dict], posts: List[Dict]) -> None:
        """Store search results in database."""
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession

        from core.db import get_db
        from models.post import Post

        async with AsyncSession(bind=await get_db().__anext__()) as db:
            for post in posts:
                result = await db.execute(select(Post).where(Post.id == post["id"]))
                existing_post = result.scalar_one_or_none()

                if not existing_post:
                    embedding = post.get("embedding")
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
                        embedding=embedding.tolist()
                        if embedding is not None and len(embedding) > 0
                        else None,
                    )
                    db.add(post_record)

            await db.commit()

    def _public_posts(self, posts: List[Dict]) -> List[Dict]:
        """Drop numpy embeddings and make values JSON-safe."""
        public = []
        for post in posts:
            created = post.get("created_utc")
            if isinstance(created, datetime):
                created = created.isoformat()

            ranking = post.get("ranking_scores")
            public_ranking = None
            if isinstance(ranking, dict):
                public_ranking = {
                    key: _to_float(value)
                    for key, value in ranking.items()
                    if key != "weights"
                }

            public.append(
                {
                    "id": post["id"],
                    "title": post["title"],
                    "selftext": post.get("selftext", ""),
                    "author": post.get("author"),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "url": post.get("url") or post.get("permalink"),
                    "permalink": post.get("permalink"),
                    "created_utc": created,
                    "subreddit": post.get("subreddit"),
                    "upvote_ratio": post.get("upvote_ratio"),
                    "ranking_scores": public_ranking,
                }
            )
        return public

    def _get_candidate_subreddits(self, search_terms: List[str]) -> List[str]:
        """Get candidate subreddits based on search terms."""
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
