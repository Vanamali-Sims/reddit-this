"""
Text embedding utilities using sentence-transformers.
"""

import asyncio
import logging
from typing import List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from core.config import settings

logger = logging.getLogger(__name__)

# Global model instance
_model: Optional[SentenceTransformer] = None


def _load_model() -> SentenceTransformer:
    """Load the embedding model."""
    global _model
    if _model is None:
        logger.info("Loading E5-small-v2 embedding model...")
        _model = SentenceTransformer("intfloat/e5-small-v2")
        logger.info("Embedding model loaded successfully")
    return _model


def _create_mock_embedding(text: str) -> np.ndarray:
    """Create a mock embedding for development."""
    # Create a deterministic embedding based on text hash
    import hashlib

    hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
    np.random.seed(hash_value % (2**32))
    return np.random.normal(0, 1, settings.EMBEDDING_DIMENSION).astype(np.float32)


async def embed_texts(texts: List[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        Numpy array of embeddings with shape (len(texts), embedding_dim)
    """
    if not texts:
        return np.array([]).reshape(0, settings.EMBEDDING_DIMENSION)

    if settings.USE_EMBEDDING_MOCK:
        logger.info(f"Using mock embeddings for {len(texts)} texts")
        embeddings = np.array([_create_mock_embedding(text) for text in texts])
        return embeddings

    # Run model inference in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(
        None, _generate_embeddings_sync, texts
    )
    return embeddings


def _generate_embeddings_sync(texts: List[str]) -> np.ndarray:
    """Synchronous embedding generation."""
    model = _load_model()

    # Preprocess texts for E5 model (add 'query:' prefix for search queries)
    processed_texts = [f"query: {text}" if len(texts) == 1 else text for text in texts]

    embeddings = model.encode(
        processed_texts,
        normalize_embeddings=True,
        show_progress_bar=len(texts) > 10,
    )
    return embeddings


async def embed_single_text(text: str) -> np.ndarray:
    """
    Generate embedding for a single text.

    Args:
        text: Text string to embed

    Returns:
        Numpy array embedding with shape (embedding_dim,)
    """
    embeddings = await embed_texts([text])
    return embeddings[0] if len(embeddings) > 0 else np.array([])


async def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Calculate cosine similarity between two embeddings.

    Args:
        a: First embedding
        b: Second embedding

    Returns:
        Cosine similarity score between -1 and 1
    """
    if len(a) == 0 or len(b) == 0:
        return 0.0

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))
