"""
Post ranking algorithms for semantic search results.
"""

import math
from datetime import datetime, timezone
from typing import Dict, List

import numpy as np


def calculate_recency_score(created_utc: datetime, center_months: int = 9, width_months: int = 6) -> float:
    """
    Calculate recency score using sigmoid function.

    Args:
        created_utc: Post creation time
        center_months: Center of sigmoid (months ago)
        width_months: Width of sigmoid transition

    Returns:
        Recency score between 0 and 1
    """
    if not created_utc:
        return 0.0

    now = datetime.now(timezone.utc)
    months_ago = (now - created_utc).days / 30.44  # Average days per month

    # Sigmoid function centered at center_months
    x = (months_ago - center_months) / width_months
    return 1 / (1 + math.exp(x))


def normalize_subreddit_score(score: int, subreddit_stats: Dict[str, Dict]) -> float:
    """
    Normalize score within subreddit context to avoid mega-sub bias.

    Args:
        score: Raw post score
        subreddit_stats: Dictionary with subreddit statistics

    Returns:
        Normalized score between 0 and 1
    """
    if not subreddit_stats:
        return min(max(score / 100.0, 0), 1)

    mean_score = subreddit_stats.get("mean_score", 10)
    std_score = subreddit_stats.get("std_score", 5)

    # Z-score normalization with clipping
    if std_score > 0:
        z_score = (score - mean_score) / std_score
        # Convert to 0-1 scale using sigmoid
        return 1 / (1 + math.exp(-z_score))
    else:
        return 0.5


def normalize_comments_score(num_comments: int, subreddit_stats: Dict[str, Dict]) -> float:
    """
    Normalize comment count within subreddit context.

    Args:
        num_comments: Number of comments
        subreddit_stats: Dictionary with subreddit statistics

    Returns:
        Normalized comment score between 0 and 1
    """
    if not subreddit_stats:
        return min(max(num_comments / 50.0, 0), 1)

    mean_comments = subreddit_stats.get("mean_comments", 5)
    std_comments = subreddit_stats.get("std_comments", 3)

    # Z-score normalization with sigmoid
    if std_comments > 0:
        z_score = (num_comments - mean_comments) / std_comments
        return 1 / (1 + math.exp(-z_score))
    else:
        return 0.5


def calculate_composite_score(
    semantic_similarity: float,
    created_utc: datetime,
    subreddit_quality: float,
    post_score: int,
    num_comments: int,
    subreddit_stats: Dict[str, Dict] = None,
) -> Dict[str, float]:
    """
    Calculate composite ranking score using weighted factors.

    Weights:
    - 45% semantic similarity
    - 20% recency
    - 15% subreddit quality
    - 10% normalized post score
    - 10% normalized comment count

    Args:
        semantic_similarity: Cosine similarity score (0-1)
        created_utc: Post creation time
        subreddit_quality: Quality score of subreddit (0-1)
        post_score: Raw Reddit post score
        num_comments: Number of comments
        subreddit_stats: Optional subreddit statistics for normalization

    Returns:
        Dictionary with breakdown of scores
    """
    weights = {
        "semantic": 0.45,
        "recency": 0.20,
        "subreddit_quality": 0.15,
        "score": 0.10,
        "comments": 0.10,
    }

    # Calculate individual components
    recency_score = calculate_recency_score(created_utc)
    score_norm = normalize_subreddit_score(post_score, subreddit_stats or {})
    comments_norm = normalize_comments_score(num_comments, subreddit_stats or {})

    # Calculate weighted composite score
    composite = (
        weights["semantic"] * semantic_similarity
        + weights["recency"] * recency_score
        + weights["subreddit_quality"] * subreddit_quality
        + weights["score"] * score_norm
        + weights["comments"] * comments_norm
    )

    return {
        "composite": composite,
        "semantic_similarity": semantic_similarity,
        "recency_score": recency_score,
        "subreddit_quality": subreddit_quality,
        "score_normalized": score_norm,
        "comments_normalized": comments_norm,
        "weights": weights,
    }


class PostRanker:
    """Rank posts using composite scoring algorithm."""

    def __init__(self):
        self.subreddit_stats: Dict[str, Dict] = {}

    def update_subreddit_stats(self, subreddit: str, posts: List[Dict]) -> None:
        """Update statistics for a subreddit based on posts."""
        if not posts:
            return

        scores = [p.get("score", 0) for p in posts]
        comments = [p.get("num_comments", 0) for p in posts]

        self.subreddit_stats[subreddit] = {
            "mean_score": np.mean(scores),
            "std_score": np.std(scores),
            "mean_comments": np.mean(comments),
            "std_comments": np.std(comments),
            "post_count": len(posts),
        }

    def rank_posts(
        self,
        posts: List[Dict],
        query_embedding: np.ndarray,
        subreddit_qualities: Dict[str, float] = None,
    ) -> List[Dict]:
        """
        Rank posts using composite scoring.

        Args:
            posts: List of post dictionaries with embeddings
            query_embedding: Query embedding for semantic similarity
            subreddit_qualities: Optional subreddit quality scores

        Returns:
            Ranked list of posts with scores
        """
        if not posts or len(query_embedding) == 0:
            return posts

        ranked_posts = []
        subreddit_qualities = subreddit_qualities or {}

        for post in posts:
            # Calculate semantic similarity
            post_embedding = post.get("embedding", np.array([]))
            if len(post_embedding) == 0:
                semantic_sim = 0.0
            else:
                semantic_sim = self._cosine_similarity(query_embedding, post_embedding)

            # Get subreddit quality
            subreddit = post.get("subreddit", "")
            subreddit_quality = subreddit_qualities.get(subreddit, 0.5)

            # Calculate composite score
            scores = calculate_composite_score(
                semantic_similarity=semantic_sim,
                created_utc=post.get("created_utc"),
                subreddit_quality=subreddit_quality,
                post_score=post.get("score", 0),
                num_comments=post.get("num_comments", 0),
                subreddit_stats=self.subreddit_stats.get(subreddit),
            )

            # Add scores to post
            post_with_scores = {**post, "ranking_scores": scores}
            ranked_posts.append(post_with_scores)

        # Sort by composite score (descending)
        ranked_posts.sort(key=lambda x: x["ranking_scores"]["composite"], reverse=True)

        return ranked_posts

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) == 0 or len(b) == 0:
            return 0.0

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(dot_product / (norm_a * norm_b))
