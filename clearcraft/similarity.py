"""
Semantic similarity checking using sentence transformers.

Uses sentence-transformers for encoding text and computing cosine similarity.
Falls back to Jaccard similarity when encoders are unavailable.
"""

import warnings
from typing import List, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    warnings.warn("sentence-transformers not available, using fallback similarity")

from clearcraft.config import settings
from clearcraft.exceptions import ClearCraftError


class SimilarityChecker:
    """Checks semantic similarity between texts."""

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize similarity checker.

        Args:
            model_name: Sentence transformer model name. Uses config default if None.
        """
        self.model_name = model_name or settings.sentence_transformer_model
        self.model: Optional[SentenceTransformer] = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                warnings.warn(
                    f"Failed to load sentence transformer model: {e}. "
                    "Using fallback similarity."
                )
                self.model = None

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute semantic similarity between two texts.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Similarity score (0.0-1.0).

        Raises:
            ClearCraftError: If similarity computation fails.
        """
        try:
            if self.model is not None:
                return self._compute_transformer_similarity(text1, text2)
            else:
                return self._compute_jaccard_similarity(text1, text2)
        except Exception as e:
            raise ClearCraftError(f"Similarity computation failed: {str(e)}") from e

    def compute_block_similarities(
        self,
        original_blocks: List[str],
        rewritten_blocks: List[str],
    ) -> List[float]:
        """
        Compute similarities for multiple text blocks.

        Args:
            original_blocks: Original text blocks.
            rewritten_blocks: Rewritten text blocks.

        Returns:
            List of similarity scores.

        Raises:
            ClearCraftError: If block counts don't match or computation fails.
        """
        if len(original_blocks) != len(rewritten_blocks):
            raise ClearCraftError(
                f"Block count mismatch: {len(original_blocks)} != {len(rewritten_blocks)}"
            )

        similarities = []
        for orig, rewritten in zip(original_blocks, rewritten_blocks):
            sim = self.compute_similarity(orig, rewritten)
            similarities.append(sim)

        return similarities

    def _compute_transformer_similarity(self, text1: str, text2: str) -> float:
        """
        Compute similarity using sentence transformers.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Cosine similarity (0.0-1.0).
        """
        assert self.model is not None

        # Encode texts
        embeddings = self.model.encode([text1, text2])

        # Compute cosine similarity
        similarity_matrix = cosine_similarity(
            embeddings[0].reshape(1, -1),
            embeddings[1].reshape(1, -1),
        )

        return float(similarity_matrix[0][0])

    def _compute_jaccard_similarity(self, text1: str, text2: str) -> float:
        """
        Compute Jaccard similarity as fallback.

        Args:
            text1: First text.
            text2: Second text.

        Returns:
            Jaccard similarity (0.0-1.0).
        """
        # Tokenize and lowercase
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())

        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity: intersection / union
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union)

    def check_threshold(
        self,
        original: str,
        rewritten: str,
        threshold: float,
    ) -> Tuple[bool, float]:
        """
        Check if similarity meets threshold.

        Args:
            original: Original text.
            rewritten: Rewritten text.
            threshold: Minimum similarity threshold.

        Returns:
            Tuple of (meets_threshold, similarity_score).
        """
        similarity = self.compute_similarity(original, rewritten)
        meets_threshold = similarity >= threshold

        return meets_threshold, similarity

    def compute_average_similarity(
        self,
        original_blocks: List[str],
        rewritten_blocks: List[str],
    ) -> float:
        """
        Compute average similarity across blocks.

        Args:
            original_blocks: Original text blocks.
            rewritten_blocks: Rewritten text blocks.

        Returns:
            Average similarity score.
        """
        similarities = self.compute_block_similarities(original_blocks, rewritten_blocks)
        return float(np.mean(similarities)) if similarities else 0.0


def check_ner_preservation(original: str, rewritten: str) -> bool:
    """
    Check if named entities are preserved (simple version).

    This is a basic check - can be enhanced with spaCy NER.

    Args:
        original: Original text.
        rewritten: Rewritten text.

    Returns:
        True if key entities appear to be preserved.
    """
    # Extract capitalized words (simple NER proxy)
    import re

    original_caps = set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", original))
    rewritten_caps = set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", rewritten))

    if not original_caps:
        return True  # No entities to preserve

    # Check preservation ratio
    preserved = original_caps & rewritten_caps
    preservation_ratio = len(preserved) / len(original_caps)

    # At least 80% of entities should be preserved
    return preservation_ratio >= 0.8
