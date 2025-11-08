#!/usr/bin/env python3
"""
Integration test for ClearCraft.

Tests the complete stack: analysis, rewriting, API, and quality guardrails.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clearcraft.analysis import TextAnalyzer
from clearcraft.selector import TextSelector
from clearcraft.similarity import SimilarityChecker
from clearcraft.exceptions import (
    SimilarityViolationError,
    ChangeRatioViolationError,
)


class TestColors:
    """Terminal colors for test output."""

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


def print_test(name: str) -> None:
    """Print test name."""
    print(f"\n{TestColors.BLUE}▶ {name}{TestColors.RESET}")


def print_success(message: str) -> None:
    """Print success message."""
    print(f"{TestColors.GREEN}  ✓ {message}{TestColors.RESET}")


def print_error(message: str) -> None:
    """Print error message."""
    print(f"{TestColors.RED}  ✗ {message}{TestColors.RESET}")


def print_info(message: str) -> None:
    """Print info message."""
    print(f"{TestColors.YELLOW}  ℹ {message}{TestColors.RESET}")


def test_text_analysis() -> bool:
    """Test text analysis functionality."""
    print_test("Testing Text Analysis")

    try:
        analyzer = TextAnalyzer()

        # Test simple text
        text = "This is a simple test. This is another sentence."
        result = analyzer.analyze(text)

        assert result.metrics.sentence_count == 2, "Sentence count mismatch"
        assert result.metrics.total_words > 0, "No words counted"
        assert 0 <= result.metrics.flesch_reading_ease <= 100, "Invalid Flesch score"
        assert result.metrics.ttr > 0, "TTR should be > 0"

        print_success("Basic analysis works")

        # Test complex text
        complex_text = """
        The implementation of sophisticated algorithmic methodologies necessitates
        comprehensive understanding. The report was written by researchers.
        """

        result = analyzer.analyze(complex_text)
        assert result.metrics.passive_ratio > 0, "Should detect passive voice"

        print_success("Passive voice detection works")
        print_success("Text analysis: PASSED")

        return True

    except Exception as e:
        print_error(f"Text analysis failed: {e}")
        return False


def test_semantic_similarity() -> bool:
    """Test semantic similarity checking."""
    print_test("Testing Semantic Similarity")

    try:
        checker = SimilarityChecker()

        # Test identical texts
        text = "This is a test sentence."
        similarity = checker.compute_similarity(text, text)
        assert similarity > 0.99, f"Identical texts should have ~1.0 similarity, got {similarity}"

        print_success("Identical text similarity works")

        # Test similar texts
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "A fast brown fox leaps over a lazy dog."
        similarity = checker.compute_similarity(text1, text2)
        assert 0.5 < similarity < 1.0, f"Similar texts should have moderate similarity, got {similarity}"

        print_success("Paraphrase similarity works")

        # Test dissimilar texts
        text1 = "Machine learning is fascinating."
        text2 = "The weather is nice today."
        similarity = checker.compute_similarity(text1, text2)
        assert similarity < 0.5, f"Dissimilar texts should have low similarity, got {similarity}"

        print_success("Dissimilar text detection works")
        print_success("Semantic similarity: PASSED")

        return True

    except Exception as e:
        print_error(f"Semantic similarity failed: {e}")
        return False


def test_deterministic_rewriting() -> bool:
    """Test deterministic rewriting pipeline."""
    print_test("Testing Deterministic Rewriting")

    try:
        selector = TextSelector(enable_llm=False)

        # Test basic rewriting
        text = "The report was written by the team. Subsequently, the methodology was utilized."

        result = selector.rewrite(text, enable_disclosure=False)

        assert result.rewritten_text != text, "Text should be modified"
        assert result.overall_similarity > 0.5, "Similarity should be reasonable"
        assert len(result.change_operations) > 0, "Should have change operations"

        print_success("Basic rewriting works")
        print_info(f"Similarity: {result.overall_similarity:.1%}")
        print_info(f"Change ratio: {result.total_change_ratio:.1%}")
        print_info(f"Operations: {len(result.change_operations)}")

        # Test metrics improvement
        assert result.rewritten_metrics.passive_ratio <= result.original_metrics.passive_ratio, \
            "Passive voice should decrease or stay same"

        print_success("Metrics improvement verified")
        print_success("Deterministic rewriting: PASSED")

        return True

    except Exception as e:
        print_error(f"Deterministic rewriting failed: {e}")
        return False


def test_citation_preservation() -> bool:
    """Test that citations and code are preserved."""
    print_test("Testing Citation Preservation")

    try:
        selector = TextSelector(enable_llm=False)

        text = """
        The study (Smith et al., 2020) shows results [1]. See https://example.com for details.

        ```python
        def example():
            return "code"
        ```
        """

        result = selector.rewrite(text, enable_disclosure=False)

        # Check citations preserved
        assert "(Smith et al., 2020)" in result.rewritten_text, "Academic citation not preserved"
        assert "[1]" in result.rewritten_text, "Reference marker not preserved"
        assert "https://example.com" in result.rewritten_text, "URL not preserved"
        assert "```python" in result.rewritten_text, "Code fence not preserved"
        assert 'def example()' in result.rewritten_text, "Code content not preserved"

        print_success("Academic citations preserved")
        print_success("Reference markers preserved")
        print_success("URLs preserved")
        print_success("Code blocks preserved")
        print_success("Citation preservation: PASSED")

        return True

    except Exception as e:
        print_error(f"Citation preservation failed: {e}")
        return False


def test_quality_guardrails() -> bool:
    """Test quality guardrails enforcement."""
    print_test("Testing Quality Guardrails")

    try:
        # Test similarity threshold enforcement
        selector = TextSelector(
            similarity_min=0.999,  # Very strict
            enable_llm=False,
        )

        text = "Utilize this sophisticated methodology to facilitate optimization."

        try:
            result = selector.rewrite(text)
            # If it succeeds, check it meets the threshold
            assert result.overall_similarity >= 0.999, \
                f"Should meet strict similarity: {result.overall_similarity}"
            print_success("Similarity threshold enforced (changes minimal)")

        except SimilarityViolationError as e:
            # Also acceptable - guardrail working
            print_success(f"Similarity guardrail triggered correctly: {e.similarity:.3f}")

        # Test change ratio cap
        selector = TextSelector(
            max_change_ratio=0.05,  # Very strict
            enable_llm=False,
        )

        try:
            result = selector.rewrite(text)
            assert result.total_change_ratio <= 0.05, \
                f"Should respect change ratio: {result.total_change_ratio}"
            print_success("Change ratio cap enforced (changes minimal)")

        except ChangeRatioViolationError as e:
            # Also acceptable - guardrail working
            print_success(f"Change ratio guardrail triggered correctly: {e.change_ratio:.3f}")

        print_success("Quality guardrails: PASSED")

        return True

    except Exception as e:
        print_error(f"Quality guardrails failed: {e}")
        return False


def test_different_tones() -> bool:
    """Test different tone settings."""
    print_test("Testing Different Tones")

    try:
        selector = TextSelector(enable_llm=False)

        text = "The implementation was undertaken to facilitate optimization."

        # Test all tones
        for tone in ["neutral", "academic", "conversational"]:
            result = selector.rewrite(text, tone=tone, enable_disclosure=False)
            assert result.rewritten_text, f"Rewriting failed for tone: {tone}"
            print_success(f"Tone '{tone}' works")

        print_success("Different tones: PASSED")

        return True

    except Exception as e:
        print_error(f"Different tones failed: {e}")
        return False


def test_disclosure_message() -> bool:
    """Test disclosure message feature."""
    print_test("Testing Disclosure Message")

    try:
        selector = TextSelector(enable_llm=False)
        text = "This is a test."

        # With disclosure
        result_with = selector.rewrite(text, enable_disclosure=True)
        assert result_with.disclosure_added, "Disclosure should be added"
        assert "AI assistance" in result_with.rewritten_text, "Disclosure text missing"

        print_success("Disclosure message added correctly")

        # Without disclosure
        result_without = selector.rewrite(text, enable_disclosure=False)
        assert not result_without.disclosure_added, "Disclosure should not be added"
        assert "AI assistance" not in result_without.rewritten_text, "Disclosure text present"

        print_success("Disclosure can be disabled")
        print_success("Disclosure message: PASSED")

        return True

    except Exception as e:
        print_error(f"Disclosure message failed: {e}")
        return False


def test_complete_workflow() -> bool:
    """Test complete analysis → rewrite workflow."""
    print_test("Testing Complete Workflow")

    try:
        # Complex text with multiple issues
        text = """
        The utilization of sophisticated methodologies was undertaken by researchers
        to facilitate the optimization of complex paradigms. Actually, the implementation
        basically requires comprehensive understanding. The findings were presented by
        the team to demonstrate efficacy.
        """

        # Step 1: Analyze
        analyzer = TextAnalyzer()
        analysis = analyzer.analyze(text)

        print_info(f"Original Flesch: {analysis.metrics.flesch_reading_ease:.1f}")
        print_info(f"Original Passive: {analysis.metrics.passive_ratio:.1%}")
        print_info(f"Original Repetition: {analysis.metrics.repetition_ratio:.1%}")

        # Step 2: Rewrite
        selector = TextSelector(enable_llm=False)
        result = selector.rewrite(text, enable_disclosure=False)

        # Step 3: Verify improvements
        print_info(f"Improved Flesch: {result.rewritten_metrics.flesch_reading_ease:.1f}")
        print_info(f"Improved Passive: {result.rewritten_metrics.passive_ratio:.1%}")
        print_info(f"Improved Repetition: {result.rewritten_metrics.repetition_ratio:.1%}")

        # Check some improvement occurred
        assert result.rewritten_text != text, "Text should be modified"
        assert result.overall_similarity > 0.80, "Should maintain good similarity"

        print_success("Analysis → Rewrite workflow works")
        print_success(f"Applied {len(result.change_operations)} transformations")
        print_success("Complete workflow: PASSED")

        return True

    except Exception as e:
        print_error(f"Complete workflow failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print(f"\n{TestColors.BLUE}{'=' * 60}{TestColors.RESET}")
    print(f"{TestColors.BLUE}ClearCraft Integration Tests{TestColors.RESET}")
    print(f"{TestColors.BLUE}{'=' * 60}{TestColors.RESET}")

    tests = [
        ("Text Analysis", test_text_analysis),
        ("Semantic Similarity", test_semantic_similarity),
        ("Deterministic Rewriting", test_deterministic_rewriting),
        ("Citation Preservation", test_citation_preservation),
        ("Quality Guardrails", test_quality_guardrails),
        ("Different Tones", test_different_tones),
        ("Disclosure Message", test_disclosure_message),
        ("Complete Workflow", test_complete_workflow),
    ]

    results = []

    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print_error(f"Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print(f"\n{TestColors.BLUE}{'=' * 60}{TestColors.RESET}")
    print(f"{TestColors.BLUE}Test Summary{TestColors.RESET}")
    print(f"{TestColors.BLUE}{'=' * 60}{TestColors.RESET}\n")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for name, passed in results:
        status = f"{TestColors.GREEN}PASSED{TestColors.RESET}" if passed else f"{TestColors.RED}FAILED{TestColors.RESET}"
        print(f"  {name}: {status}")

    print(f"\n{TestColors.BLUE}Results: {passed_count}/{total_count} tests passed{TestColors.RESET}")

    if passed_count == total_count:
        print(f"\n{TestColors.GREEN}✓ All integration tests passed!{TestColors.RESET}\n")
        return 0
    else:
        print(f"\n{TestColors.RED}✗ Some tests failed{TestColors.RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
