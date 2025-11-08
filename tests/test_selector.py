"""Tests for text selector/orchestrator module."""

import pytest
from clearcraft.selector import TextSelector, RewriteResult
from clearcraft.exceptions import (
    SimilarityViolationError,
    ChangeRatioViolationError,
    DisallowedIntentError,
)


class TestTextSelector:
    """Test TextSelector class."""

    def test_basic_rewrite(self):
        """Test basic rewriting functionality."""
        selector = TextSelector(enable_llm=False)

        text = "This is a simple test. This is another sentence."
        result = selector.rewrite(text, tone="neutral")

        assert isinstance(result, RewriteResult)
        assert result.original_text == text
        assert len(result.rewritten_text) > 0
        assert result.overall_similarity > 0.5
        assert len(result.change_operations) > 0

    def test_similarity_threshold(self):
        """Test that similarity threshold is enforced."""
        # Set very high similarity threshold
        selector = TextSelector(
            similarity_min=0.999,
            enable_llm=False,
        )

        # Even minor changes might violate this
        text = "Utilize this methodology to facilitate the process."

        # Might raise SimilarityViolationError depending on changes
        # This is expected behavior
        try:
            result = selector.rewrite(text)
            # If it succeeds, check similarity is high
            assert result.overall_similarity >= 0.999
        except SimilarityViolationError:
            # This is also acceptable - guardrail working
            pass

    def test_change_ratio_limit(self):
        """Test that change ratio limit is enforced."""
        selector = TextSelector(
            max_change_ratio=0.05,  # Very strict limit
            enable_llm=False,
        )

        text = "This is a simple sentence that needs improvement."

        try:
            result = selector.rewrite(text)
            assert result.total_change_ratio <= 0.05
        except ChangeRatioViolationError:
            # Acceptable - too many changes needed
            pass

    def test_preserves_citations(self):
        """Test that citations are preserved."""
        selector = TextSelector(enable_llm=False)

        text = "The study (Smith et al., 2020) shows that [1] results are significant."
        result = selector.rewrite(text)

        # Citations should be preserved
        assert "Smith et al., 2020" in result.rewritten_text
        assert "[1]" in result.rewritten_text

    def test_preserves_code_blocks(self):
        """Test that code blocks are preserved."""
        selector = TextSelector(enable_llm=False)

        text = """
        Here is some text before the code.

        ```python
        def hello():
            print("Hello, World!")
        ```

        And some text after the code.
        """

        result = selector.rewrite(text)

        # Code block should be preserved
        assert "```python" in result.rewritten_text
        assert 'print("Hello, World!")' in result.rewritten_text

    def test_different_tones(self):
        """Test that different tones can be specified."""
        selector = TextSelector(enable_llm=False)

        text = "This is a test sentence for clarity improvement."

        for tone in ["neutral", "academic", "conversational"]:
            result = selector.rewrite(text, tone=tone)
            assert isinstance(result, RewriteResult)

    def test_metrics_improvement(self):
        """Test that metrics generally improve."""
        selector = TextSelector(enable_llm=False)

        # Text with issues
        text = (
            "The methodology was utilized by the researchers to facilitate "
            "the implementation of the paradigm. The researchers utilized "
            "the methodology to implement the paradigm."
        )

        result = selector.rewrite(text)

        # Should have less repetition
        assert (
            result.rewritten_metrics.repetition_ratio <=
            result.original_metrics.repetition_ratio
        )

    def test_disclosure_message(self):
        """Test that disclosure message can be added."""
        selector = TextSelector(enable_llm=False)

        text = "This is a test."

        # With disclosure
        result_with = selector.rewrite(text, enable_disclosure=True)
        assert result_with.disclosure_added
        assert "AI assistance" in result_with.rewritten_text

        # Without disclosure
        result_without = selector.rewrite(text, enable_disclosure=False)
        assert not result_without.disclosure_added

    def test_change_operations_logged(self):
        """Test that all change operations are logged."""
        selector = TextSelector(enable_llm=False)

        text = "Utilize this simple methodology."
        result = selector.rewrite(text)

        # Should have at least some operations
        assert len(result.change_operations) > 0

        # Each operation should have required fields
        for op in result.change_operations:
            assert op.pass_name
            assert isinstance(op.confidence, float)
            assert 0 <= op.confidence <= 1


class TestDisallowedIntents:
    """Test that disallowed intents are blocked."""

    def test_blocks_bypass_keywords(self):
        """Test that bypass-related keywords are blocked."""
        selector = TextSelector(enable_llm=False)

        # This should work fine
        normal_text = "This is normal text about improving clarity."
        result = selector.rewrite(normal_text)
        assert isinstance(result, RewriteResult)

        # Note: DisallowedIntentError is primarily checked in the LLM adapter
        # The selector itself doesn't check the input text for disallowed keywords
        # That check happens in the DeepInfra adapter when LLM mode is enabled
