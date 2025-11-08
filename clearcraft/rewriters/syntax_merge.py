"""
Sentence merging for ultra-short sentences.

Merges very short consecutive sentences when safe to do so,
improving flow and reducing choppiness.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class MergeOperation:
    """Record of a merge operation."""

    originals: List[str]
    merged: str
    confidence: float
    reason: str


class SyntaxMerger:
    """Merges ultra-short sentences for better flow."""

    def __init__(self, min_length: int = 5):
        """
        Initialize merger.

        Args:
            min_length: Minimum sentence length in tokens before considering merge.
        """
        self.min_length = min_length

    def can_merge(self, sent1: str, sent2: str) -> Tuple[bool, float, str]:
        """
        Check if two sentences can be safely merged.

        Args:
            sent1: First sentence.
            sent2: Second sentence.

        Returns:
            Tuple of (can_merge, confidence, reason).
        """
        # Both must be short
        tokens1 = sent1.split()
        tokens2 = sent2.split()

        if len(tokens1) > self.min_length and len(tokens2) > self.min_length:
            return False, 0.0, "both_too_long"

        # Check for subject continuity (simple heuristic)
        # Look for pronouns at start of second sentence
        pronouns = ["it", "this", "that", "they", "these", "those", "he", "she"]
        first_word = tokens2[0].lower() if tokens2 else ""

        if first_word in pronouns:
            return True, 0.85, "pronoun_continuation"

        # Check for coordinating conjunction
        conjunctions = ["and", "but", "or", "so", "yet"]
        if first_word in conjunctions:
            return True, 0.80, "coordinating_conjunction"

        # Check for simple enumeration/listing
        if len(tokens1) <= 3 and len(tokens2) <= 3:
            return True, 0.70, "short_enumeration"

        # Default: merge if both are very short
        if len(tokens1) <= self.min_length and len(tokens2) <= self.min_length:
            return True, 0.60, "both_short"

        return False, 0.0, "no_merge_pattern"

    def merge_sentences(self, sent1: str, sent2: str, reason: str) -> str:
        """
        Merge two sentences.

        Args:
            sent1: First sentence.
            sent2: Second sentence.
            reason: Reason for merge.

        Returns:
            Merged sentence.
        """
        # Remove ending punctuation from first sentence
        sent1 = sent1.rstrip(".!?")

        # Check if second sentence starts with conjunction
        tokens2 = sent2.split()
        first_word = tokens2[0].lower() if tokens2 else ""

        if first_word in ["and", "but", "or", "so", "yet"]:
            # Keep conjunction, lowercase if appropriate
            merged = f"{sent1}, {sent2}"
        else:
            # Add "and" connector
            merged = f"{sent1} and {sent2.lower()}"

        return merged

    def process(self, text: str) -> Tuple[str, List[MergeOperation]]:
        """
        Process text and merge ultra-short sentences.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, operations).
        """
        sentences = self._split_sentences(text)
        operations: List[MergeOperation] = []
        result_sentences: List[str] = []

        i = 0
        while i < len(sentences):
            if i + 1 < len(sentences):
                can_merge, confidence, reason = self.can_merge(
                    sentences[i],
                    sentences[i + 1],
                )

                if can_merge and confidence >= 0.60:
                    # Merge
                    merged = self.merge_sentences(sentences[i], sentences[i + 1], reason)
                    operations.append(
                        MergeOperation(
                            originals=[sentences[i], sentences[i + 1]],
                            merged=merged,
                            confidence=confidence,
                            reason=reason,
                        )
                    )
                    result_sentences.append(merged)
                    i += 2  # Skip both sentences
                    continue

            # No merge, keep original
            result_sentences.append(sentences[i])
            i += 1

        # Reconstruct text
        processed_text = " ".join(result_sentences)

        return processed_text, operations

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text.

        Returns:
            List of sentences.
        """
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
