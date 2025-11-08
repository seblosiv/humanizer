"""
Sentence splitting for overly long sentences.

Splits sentences at safe boundaries (conjunctions, semicolons, etc.)
while maintaining grammatical correctness.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class SplitOperation:
    """Record of a split operation."""

    original: str
    split_sentences: List[str]
    confidence: float
    reason: str


class SyntaxSplitter:
    """Splits long sentences at safe boundaries."""

    # Safe split patterns with coordinating conjunctions
    SPLIT_PATTERNS = [
        # Semicolon
        (re.compile(r";\s+"), ". ", 0.95, "semicolon"),
        # Coordinating conjunctions with comma
        (re.compile(r",\s+(and|but|or|yet|so)\s+"), r", \1 ", 0.85, "coordinating_conjunction"),
        # Em dash
        (re.compile(r"\s+—\s+"), ". ", 0.80, "em_dash"),
        # Relative clauses (which/that)
        (re.compile(r",\s+(which|that)\s+"), r". \1 ", 0.70, "relative_clause"),
    ]

    def __init__(self, max_length: int = 30):
        """
        Initialize splitter.

        Args:
            max_length: Maximum sentence length in tokens before splitting.
        """
        self.max_length = max_length

    def split_sentence(self, sentence: str) -> Optional[SplitOperation]:
        """
        Split a sentence if it's too long.

        Args:
            sentence: Input sentence.

        Returns:
            SplitOperation if split performed, None otherwise.
        """
        tokens = sentence.split()
        if len(tokens) <= self.max_length:
            return None

        # Try each split pattern in order of confidence
        for pattern, replacement, confidence, reason in self.SPLIT_PATTERNS:
            if pattern.search(sentence):
                # Perform split
                parts = pattern.split(sentence)
                if len(parts) > 1:
                    # Clean and capitalize
                    split_sentences = []
                    for i, part in enumerate(parts):
                        part = part.strip()
                        if part:
                            # Capitalize first letter
                            if i > 0:
                                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
                            # Ensure ending punctuation
                            if not part[-1] in ".!?":
                                part += "."
                            split_sentences.append(part)

                    if len(split_sentences) > 1:
                        return SplitOperation(
                            original=sentence,
                            split_sentences=split_sentences,
                            confidence=confidence,
                            reason=reason,
                        )

        return None

    def process(self, text: str) -> Tuple[str, List[SplitOperation]]:
        """
        Process text and split long sentences.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, operations).
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        operations: List[SplitOperation] = []
        result_sentences: List[str] = []

        for sentence in sentences:
            operation = self.split_sentence(sentence)
            if operation:
                operations.append(operation)
                result_sentences.extend(operation.split_sentences)
            else:
                result_sentences.append(sentence)

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
