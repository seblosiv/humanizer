"""
Orchestrator for text rewriting passes.

Coordinates deterministic rewriters and optional LLM pass,
enforcing quality guardrails and logging all changes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from clearcraft.config import settings
from clearcraft.analysis import TextAnalyzer, ReadabilityMetrics
from clearcraft.similarity import SimilarityChecker
from clearcraft.chunking import TextChunker
from clearcraft.rewriters.syntax_split import SyntaxSplitter
from clearcraft.rewriters.syntax_merge import SyntaxMerger
from clearcraft.rewriters.voice_active import VoiceActivator
from clearcraft.rewriters.jargon_plain import JargonSimplifier
from clearcraft.rewriters.repetition_trim import RepetitionTrimmer
from clearcraft.rewriters.grammar import GrammarCorrector
from clearcraft.rewriters.formatting import FormattingNormalizer
from clearcraft.exceptions import (
    SimilarityViolationError,
    ChangeRatioViolationError,
    RewriteError,
)


@dataclass
class ChangeOperation:
    """Record of a single change operation."""

    pass_name: str
    tokens_changed: int
    total_tokens: int
    confidence: float
    reason: str
    similarity_score: Optional[float] = None


@dataclass
class RewriteResult:
    """Result of complete rewrite operation."""

    original_text: str
    rewritten_text: str
    original_metrics: ReadabilityMetrics
    rewritten_metrics: ReadabilityMetrics
    change_operations: List[ChangeOperation] = field(default_factory=list)
    overall_similarity: float = 0.0
    total_change_ratio: float = 0.0
    disclosure_added: bool = False


class TextSelector:
    """Orchestrates text rewriting with quality guardrails."""

    def __init__(
        self,
        target_avg_sentence_length: Optional[tuple[int, int]] = None,
        max_change_ratio: Optional[float] = None,
        similarity_min: Optional[float] = None,
        enable_llm: bool = False,
    ):
        """
        Initialize selector.

        Args:
            target_avg_sentence_length: Tuple of (min, max) for target sentence length.
            max_change_ratio: Maximum allowed change ratio.
            similarity_min: Minimum semantic similarity threshold.
            enable_llm: Whether to enable optional LLM pass.
        """
        self.target_sentence_length = target_avg_sentence_length or (
            settings.target_avg_sentence_length_min,
            settings.target_avg_sentence_length_max,
        )
        self.max_change_ratio = max_change_ratio or settings.max_change_ratio
        self.similarity_min = similarity_min or settings.similarity_min
        self.enable_llm = enable_llm and settings.is_deepinfra_enabled

        # Initialize components
        self.analyzer = TextAnalyzer()
        self.similarity_checker = SimilarityChecker()
        self.chunker = TextChunker(chunk_size=settings.chunk_size)

        # Initialize rewriters
        self.syntax_splitter = SyntaxSplitter(
            max_length=self.target_sentence_length[1] + 8
        )
        self.syntax_merger = SyntaxMerger(
            min_length=self.target_sentence_length[0] - 2
        )
        self.voice_activator = VoiceActivator()
        self.jargon_simplifier = JargonSimplifier()
        self.repetition_trimmer = RepetitionTrimmer()
        self.grammar_corrector = GrammarCorrector()
        self.formatting_normalizer = FormattingNormalizer()

        # LLM adapter (lazy loaded)
        self._llm_adapter = None

    def rewrite(
        self,
        text: str,
        tone: str = "neutral",
        enable_disclosure: Optional[bool] = None,
    ) -> RewriteResult:
        """
        Rewrite text with quality guardrails.

        Args:
            text: Input text.
            tone: Desired tone (neutral/academic/conversational).
            enable_disclosure: Whether to add disclosure. Uses settings default if None.

        Returns:
            RewriteResult with original and rewritten text plus metadata.

        Raises:
            SimilarityViolationError: If similarity falls below threshold.
            ChangeRatioViolationError: If change ratio exceeds maximum.
            RewriteError: If rewriting fails.
        """
        try:
            original_text = text
            current_text = text
            change_operations: List[ChangeOperation] = []

            # Analyze original
            original_analysis = self.analyzer.analyze(original_text)
            original_metrics = original_analysis.metrics

            # Apply deterministic passes
            current_text = self._apply_deterministic_passes(
                current_text,
                original_text,
                change_operations,
            )

            # Optional LLM pass
            if self.enable_llm:
                current_text = self._apply_llm_pass(
                    current_text,
                    original_text,
                    tone,
                    change_operations,
                )

            # Final analysis
            rewritten_analysis = self.analyzer.analyze(current_text)
            rewritten_metrics = rewritten_analysis.metrics

            # Check similarity guardrail
            overall_similarity = self.similarity_checker.compute_similarity(
                original_text,
                current_text,
            )

            if overall_similarity < self.similarity_min:
                raise SimilarityViolationError(
                    similarity=overall_similarity,
                    threshold=self.similarity_min,
                )

            # Check change ratio guardrail
            total_change_ratio = self._calculate_change_ratio(
                original_text,
                current_text,
            )

            if total_change_ratio > self.max_change_ratio:
                raise ChangeRatioViolationError(
                    change_ratio=total_change_ratio,
                    max_ratio=self.max_change_ratio,
                )

            # Add disclosure if enabled
            disclosure_added = False
            if enable_disclosure if enable_disclosure is not None else settings.enable_disclosure:
                current_text += settings.get_disclosure_message()
                disclosure_added = True

            return RewriteResult(
                original_text=original_text,
                rewritten_text=current_text,
                original_metrics=original_metrics,
                rewritten_metrics=rewritten_metrics,
                change_operations=change_operations,
                overall_similarity=overall_similarity,
                total_change_ratio=total_change_ratio,
                disclosure_added=disclosure_added,
            )

        except (SimilarityViolationError, ChangeRatioViolationError):
            raise
        except Exception as e:
            raise RewriteError(f"Rewriting failed: {str(e)}") from e

    def _apply_deterministic_passes(
        self,
        text: str,
        original: str,
        operations: List[ChangeOperation],
    ) -> str:
        """
        Apply all deterministic rewriting passes.

        Args:
            text: Current text.
            original: Original text for similarity checking.
            operations: List to append operations to.

        Returns:
            Rewritten text.
        """
        # Pass 1: Formatting normalization
        text, _ = self.formatting_normalizer.process(text)
        self._record_operation("formatting", text, original, 0.95, "normalize_formatting", operations)

        # Pass 2: Grammar correction
        text, corrections = self.grammar_corrector.process(text)
        if corrections:
            self._record_operation("grammar", text, original, 0.85, f"{len(corrections)}_corrections", operations)

        # Pass 3: Sentence splitting (if avg length too high)
        text, split_ops = self.syntax_splitter.process(text)
        if split_ops:
            self._record_operation("syntax_split", text, original, 0.80, f"{len(split_ops)}_splits", operations)

        # Pass 4: Sentence merging (if avg length too low)
        text, merge_ops = self.syntax_merger.process(text)
        if merge_ops:
            self._record_operation("syntax_merge", text, original, 0.75, f"{len(merge_ops)}_merges", operations)

        # Pass 5: Passive to active voice
        text, conversions = self.voice_activator.process(text)
        if conversions:
            self._record_operation("voice_active", text, original, 0.75, f"{len(conversions)}_conversions", operations)

        # Pass 6: Jargon simplification
        text, replacements = self.jargon_simplifier.process(text)
        if replacements:
            self._record_operation("jargon_plain", text, original, 0.80, f"{len(replacements)}_replacements", operations)

        # Pass 7: Repetition trimming
        text, edits = self.repetition_trimmer.process(text)
        if edits:
            self._record_operation("repetition_trim", text, original, 0.85, f"{len(edits)}_edits", operations)

        return text

    def _apply_llm_pass(
        self,
        text: str,
        original: str,
        tone: str,
        operations: List[ChangeOperation],
    ) -> str:
        """
        Apply optional LLM pass for final polish.

        Args:
            text: Current text.
            original: Original text for similarity checking.
            tone: Desired tone.
            operations: List to append operations to.

        Returns:
            LLM-polished text.
        """
        if not self._llm_adapter:
            from clearcraft.adapters.deepinfra_llm import DeepInfraAdapter
            self._llm_adapter = DeepInfraAdapter()

        llm_result = self._llm_adapter.polish_text(
            text=text,
            tone=tone,
            max_change_ratio=self.max_change_ratio,
            similarity_min=self.similarity_min,
        )

        # Check LLM output similarity
        llm_similarity = self.similarity_checker.compute_similarity(
            text,
            llm_result,
        )

        self._record_operation(
            "llm_polish",
            llm_result,
            original,
            0.70,
            f"tone_{tone}",
            operations,
            similarity_score=llm_similarity,
        )

        return llm_result

    def _record_operation(
        self,
        pass_name: str,
        current_text: str,
        original_text: str,
        confidence: float,
        reason: str,
        operations: List[ChangeOperation],
        similarity_score: Optional[float] = None,
    ) -> None:
        """
        Record a change operation.

        Args:
            pass_name: Name of the pass.
            current_text: Text after this pass.
            original_text: Original text.
            confidence: Confidence score.
            reason: Reason for changes.
            operations: List to append to.
            similarity_score: Optional similarity score.
        """
        original_tokens = len(original_text.split())
        current_tokens = len(current_text.split())
        tokens_changed = abs(current_tokens - original_tokens)

        operations.append(
            ChangeOperation(
                pass_name=pass_name,
                tokens_changed=tokens_changed,
                total_tokens=original_tokens,
                confidence=confidence,
                reason=reason,
                similarity_score=similarity_score,
            )
        )

    def _calculate_change_ratio(self, original: str, rewritten: str) -> float:
        """
        Calculate overall change ratio using Levenshtein-like metric.

        Args:
            original: Original text.
            rewritten: Rewritten text.

        Returns:
            Change ratio (0.0-1.0).
        """
        original_words = original.split()
        rewritten_words = rewritten.split()

        # Simple word-level diff
        max_len = max(len(original_words), len(rewritten_words))
        if max_len == 0:
            return 0.0

        # Count differences
        differences = 0
        for i in range(min(len(original_words), len(rewritten_words))):
            if original_words[i] != rewritten_words[i]:
                differences += 1

        # Add extra words as differences
        differences += abs(len(original_words) - len(rewritten_words))

        return differences / max_len
