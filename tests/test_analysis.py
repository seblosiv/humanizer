"""Tests for text analysis module."""

import pytest
from clearcraft.analysis import TextAnalyzer, ReadabilityMetrics
from clearcraft.exceptions import AnalysisError


class TestTextAnalyzer:
    """Test TextAnalyzer class."""

    def test_analyze_simple_text(self):
        """Test analysis of simple text."""
        analyzer = TextAnalyzer()
        text = "This is a simple sentence. This is another sentence."

        result = analyzer.analyze(text)

        assert result.metrics.sentence_count == 2
        assert result.metrics.total_words > 0
        assert 0 <= result.metrics.flesch_reading_ease <= 100
        assert result.metrics.ttr > 0

    def test_analyze_complex_text(self):
        """Test analysis of more complex text."""
        analyzer = TextAnalyzer()
        text = """
        The implementation of sophisticated algorithmic methodologies necessitates
        comprehensive understanding of computational complexity. Consequently,
        practitioners must facilitate optimization through systematic analysis.
        """

        result = analyzer.analyze(text)

        # Complex text should have lower readability scores
        assert result.metrics.flesch_reading_ease < 60
        assert result.metrics.flesch_kincaid_grade > 10

    def test_analyze_passive_voice(self):
        """Test passive voice detection."""
        analyzer = TextAnalyzer()

        # Text with passive voice
        passive_text = "The report was written by the team. The findings were analyzed by researchers."
        result_passive = analyzer.analyze(passive_text)

        # Text with active voice
        active_text = "The team wrote the report. Researchers analyzed the findings."
        result_active = analyzer.analyze(active_text)

        # Passive text should have higher passive ratio
        assert result_passive.metrics.passive_ratio > result_active.metrics.passive_ratio

    def test_analyze_repetition(self):
        """Test repetition detection."""
        analyzer = TextAnalyzer()

        # Text with repetition
        repetitive_text = (
            "The quick brown fox jumps over the lazy dog. "
            "The quick brown fox runs fast. "
            "The quick brown fox is very quick."
        )

        result = analyzer.analyze(repetitive_text)

        assert result.metrics.repetition_ratio > 0
        assert len(result.repetitive_phrases) > 0

    def test_analyze_empty_text(self):
        """Test that empty text raises error."""
        analyzer = TextAnalyzer()

        with pytest.raises(AnalysisError):
            analyzer.analyze("")

        with pytest.raises(AnalysisError):
            analyzer.analyze("   ")

    def test_lexical_diversity(self):
        """Test lexical diversity metrics."""
        analyzer = TextAnalyzer()

        # Low diversity (repeated words)
        low_diversity = " ".join(["word"] * 100)
        result_low = analyzer.analyze(low_diversity)

        # High diversity (unique words)
        high_diversity = " ".join([f"word{i}" for i in range(100)])
        result_high = analyzer.analyze(high_diversity)

        # High diversity text should have higher TTR
        assert result_high.metrics.ttr > result_low.metrics.ttr

    def test_compare_metrics(self):
        """Test metrics comparison."""
        analyzer = TextAnalyzer()

        before_text = "This is very very very simple text with simple words."
        after_text = "This is straightforward text with clear words."

        before_result = analyzer.analyze(before_text)
        after_result = analyzer.analyze(after_text)

        comparison = analyzer.compare_metrics(
            before_result.metrics,
            after_result.metrics,
        )

        assert "flesch_reading_ease" in comparison
        assert "avg_sentence_length" in comparison
        assert "repetition_ratio" in comparison


class TestReadabilityMetrics:
    """Test ReadabilityMetrics dataclass."""

    def test_metrics_creation(self):
        """Test creating metrics object."""
        metrics = ReadabilityMetrics(
            flesch_reading_ease=65.0,
            flesch_kincaid_grade=8.0,
            gunning_fog=10.0,
            smog_index=9.0,
            sentence_count=10,
            avg_sentence_length=15.0,
            avg_word_length=5.0,
            mtld=50.0,
            ttr=0.6,
            unique_words=100,
            total_words=200,
            passive_ratio=0.1,
            repetition_ratio=0.05,
            syllable_count=300,
            complex_word_count=20,
        )

        assert metrics.flesch_reading_ease == 65.0
        assert metrics.sentence_count == 10
        assert metrics.ttr == 0.6
