"""Tests for similarity checking module."""

import pytest
from clearcraft.similarity import SimilarityChecker, check_ner_preservation


class TestSimilarityChecker:
    """Test SimilarityChecker class."""

    def test_identical_texts(self):
        """Test that identical texts have similarity of 1.0."""
        checker = SimilarityChecker()
        text = "This is a test sentence."

        similarity = checker.compute_similarity(text, text)

        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_similar_texts(self):
        """Test that similar texts have high similarity."""
        checker = SimilarityChecker()
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "A fast brown fox leaps over a lazy dog."

        similarity = checker.compute_similarity(text1, text2)

        # Should be similar but not identical
        assert 0.7 < similarity < 1.0

    def test_dissimilar_texts(self):
        """Test that dissimilar texts have low similarity."""
        checker = SimilarityChecker()
        text1 = "This is about machine learning and AI."
        text2 = "The recipe calls for flour, eggs, and sugar."

        similarity = checker.compute_similarity(text1, text2)

        # Should have low similarity
        assert similarity < 0.5

    def test_block_similarities(self):
        """Test computing similarities for multiple blocks."""
        checker = SimilarityChecker()
        originals = [
            "First sentence here.",
            "Second sentence here.",
            "Third sentence here.",
        ]
        rewritten = [
            "First statement here.",
            "Second statement here.",
            "Third statement here.",
        ]

        similarities = checker.compute_block_similarities(originals, rewritten)

        assert len(similarities) == 3
        assert all(s > 0.7 for s in similarities)

    def test_check_threshold(self):
        """Test threshold checking."""
        checker = SimilarityChecker()
        text1 = "This is a test."
        text2 = "This is a test."

        meets_threshold, similarity = checker.check_threshold(
            text1,
            text2,
            threshold=0.95,
        )

        assert meets_threshold
        assert similarity >= 0.95

    def test_average_similarity(self):
        """Test average similarity computation."""
        checker = SimilarityChecker()
        originals = ["Text one.", "Text two."]
        rewritten = ["Text one.", "Text two."]

        avg = checker.compute_average_similarity(originals, rewritten)

        assert avg == pytest.approx(1.0, abs=0.01)


class TestNERPreservation:
    """Test named entity preservation checking."""

    def test_preserves_names(self):
        """Test that proper names are preserved."""
        original = "John Smith went to New York City."
        rewritten = "John Smith traveled to New York City."

        assert check_ner_preservation(original, rewritten)

    def test_missing_names(self):
        """Test detection of missing names."""
        original = "Albert Einstein developed the theory."
        rewritten = "A scientist developed the theory."

        # Should detect missing entity
        assert not check_ner_preservation(original, rewritten)

    def test_no_entities(self):
        """Test text with no entities."""
        original = "This is a simple sentence."
        rewritten = "This is an easy sentence."

        assert check_ner_preservation(original, rewritten)
