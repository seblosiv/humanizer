"""
Text analysis module with readability metrics.

Implements:
- Flesch Reading Ease
- Flesch-Kincaid Grade Level
- Gunning Fog Index
- SMOG Index
- MTLD (Measure of Textual Lexical Diversity)
- TTR (Type-Token Ratio)
- Sentence statistics
- Passive voice detection
- Repetition analysis
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import textstat
from lexicalrichness import LexicalRichness
from clearcraft.exceptions import AnalysisError


@dataclass
class ReadabilityMetrics:
    """Container for readability metrics."""

    # Traditional readability scores
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    gunning_fog: float
    smog_index: float

    # Sentence statistics
    sentence_count: int
    avg_sentence_length: float  # in tokens
    avg_word_length: float  # in characters

    # Lexical diversity
    mtld: Optional[float]  # None if text too short
    ttr: float  # Type-Token Ratio
    unique_words: int
    total_words: int

    # Voice and style
    passive_ratio: float
    repetition_ratio: float

    # Additional metrics
    syllable_count: int
    complex_word_count: int


@dataclass
class AnalysisResult:
    """Complete analysis result."""

    metrics: ReadabilityMetrics
    sentences: List[str]
    passive_sentences: List[int]  # Indices of passive sentences
    repetitive_phrases: Dict[str, int]  # Phrase -> count


class TextAnalyzer:
    """Analyzes text for readability and style metrics."""

    def __init__(self):
        """Initialize analyzer."""
        # Common passive voice patterns
        self.passive_patterns = [
            re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+ed\b", re.IGNORECASE),
            re.compile(r"\b(is|are|was|were|be|been|being)\s+\w+en\b", re.IGNORECASE),
        ]

    def analyze(self, text: str) -> AnalysisResult:
        """
        Perform complete text analysis.

        Args:
            text: Input text to analyze.

        Returns:
            AnalysisResult with all metrics.

        Raises:
            AnalysisError: If analysis fails.
        """
        try:
            if not text or not text.strip():
                raise AnalysisError("Cannot analyze empty text")

            # Clean text for analysis
            clean_text = self._clean_text(text)

            # Get sentences
            sentences = self._split_sentences(clean_text)
            if not sentences:
                raise AnalysisError("No sentences found in text")

            # Calculate readability scores
            flesch = textstat.flesch_reading_ease(clean_text)
            fk_grade = textstat.flesch_kincaid_grade(clean_text)
            fog = textstat.gunning_fog(clean_text)
            smog = textstat.smog_index(clean_text)

            # Sentence statistics
            sentence_count = len(sentences)
            words = clean_text.split()
            total_words = len(words)
            avg_sentence_length = total_words / sentence_count if sentence_count > 0 else 0

            # Word statistics
            syllable_count = textstat.syllable_count(clean_text)
            avg_word_length = sum(len(w) for w in words) / total_words if total_words > 0 else 0
            complex_word_count = textstat.difficult_words(clean_text)

            # Lexical diversity
            unique_words = len(set(word.lower() for word in words))
            ttr = unique_words / total_words if total_words > 0 else 0

            # MTLD (requires at least 50 tokens)
            mtld_value: Optional[float] = None
            if total_words >= 50:
                try:
                    lex = LexicalRichness(clean_text)
                    mtld_value = lex.mtld(threshold=0.72)
                except Exception:
                    mtld_value = None

            # Voice and style
            passive_sentences = self._detect_passive_voice(sentences)
            passive_ratio = len(passive_sentences) / sentence_count if sentence_count > 0 else 0

            # Repetition analysis
            repetitive_phrases = self._find_repetitive_phrases(clean_text)
            repetition_ratio = self._calculate_repetition_ratio(repetitive_phrases, total_words)

            metrics = ReadabilityMetrics(
                flesch_reading_ease=flesch,
                flesch_kincaid_grade=fk_grade,
                gunning_fog=fog,
                smog_index=smog,
                sentence_count=sentence_count,
                avg_sentence_length=avg_sentence_length,
                avg_word_length=avg_word_length,
                mtld=mtld_value,
                ttr=ttr,
                unique_words=unique_words,
                total_words=total_words,
                passive_ratio=passive_ratio,
                repetition_ratio=repetition_ratio,
                syllable_count=syllable_count,
                complex_word_count=complex_word_count,
            )

            return AnalysisResult(
                metrics=metrics,
                sentences=sentences,
                passive_sentences=passive_sentences,
                repetitive_phrases=repetitive_phrases,
            )

        except AnalysisError:
            raise
        except Exception as e:
            raise AnalysisError(f"Analysis failed: {str(e)}") from e

    def _clean_text(self, text: str) -> str:
        """
        Clean text for analysis (remove markdown, etc.).

        Args:
            text: Raw text.

        Returns:
            Cleaned text.
        """
        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`[^`]+`", "", text)

        # Remove links but keep link text
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text.

        Returns:
            List of sentences.
        """
        # Simple sentence splitting (can be improved with spaCy)
        sentences = re.split(r"[.!?]+\s+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _detect_passive_voice(self, sentences: List[str]) -> List[int]:
        """
        Detect passive voice in sentences.

        Args:
            sentences: List of sentences.

        Returns:
            Indices of sentences with passive voice.
        """
        passive_indices = []

        for i, sentence in enumerate(sentences):
            for pattern in self.passive_patterns:
                if pattern.search(sentence):
                    passive_indices.append(i)
                    break

        return passive_indices

    def _find_repetitive_phrases(self, text: str) -> Dict[str, int]:
        """
        Find repetitive bigrams and trigrams.

        Args:
            text: Input text.

        Returns:
            Dictionary of phrase -> count for phrases appearing >= 3 times.
        """
        words = text.lower().split()
        phrases: Dict[str, int] = {}

        # Bigrams
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}"
            phrases[phrase] = phrases.get(phrase, 0) + 1

        # Trigrams
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
            phrases[phrase] = phrases.get(phrase, 0) + 1

        # Filter to only repetitive phrases (>= 3 occurrences)
        return {phrase: count for phrase, count in phrases.items() if count >= 3}

    def _calculate_repetition_ratio(
        self,
        repetitive_phrases: Dict[str, int],
        total_words: int,
    ) -> float:
        """
        Calculate overall repetition ratio.

        Args:
            repetitive_phrases: Dictionary of repetitive phrases.
            total_words: Total word count.

        Returns:
            Repetition ratio (0.0-1.0).
        """
        if not repetitive_phrases or total_words == 0:
            return 0.0

        # Count total repetitive tokens
        repetitive_tokens = sum(
            (count - 1) * len(phrase.split())
            for phrase, count in repetitive_phrases.items()
        )

        return min(1.0, repetitive_tokens / total_words)

    def compare_metrics(
        self,
        before: ReadabilityMetrics,
        after: ReadabilityMetrics,
    ) -> Dict[str, float]:
        """
        Compare before/after metrics.

        Args:
            before: Metrics before rewriting.
            after: Metrics after rewriting.

        Returns:
            Dictionary of metric_name -> delta.
        """
        return {
            "flesch_reading_ease": after.flesch_reading_ease - before.flesch_reading_ease,
            "flesch_kincaid_grade": after.flesch_kincaid_grade - before.flesch_kincaid_grade,
            "gunning_fog": after.gunning_fog - before.gunning_fog,
            "avg_sentence_length": after.avg_sentence_length - before.avg_sentence_length,
            "passive_ratio": after.passive_ratio - before.passive_ratio,
            "repetition_ratio": after.repetition_ratio - before.repetition_ratio,
            "ttr": after.ttr - before.ttr,
        }
