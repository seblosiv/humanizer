"""
Custom exceptions for ClearCraft.

Provides specific error types for different failure modes.
"""


class ClearCraftError(Exception):
    """Base exception for all ClearCraft errors."""

    pass


class SimilarityViolationError(ClearCraftError):
    """Raised when semantic similarity falls below threshold."""

    def __init__(
        self,
        similarity: float,
        threshold: float,
        message: str = "Semantic similarity violation",
    ):
        self.similarity = similarity
        self.threshold = threshold
        super().__init__(
            f"{message}: {similarity:.3f} < {threshold:.3f} (threshold)"
        )


class ChangeRatioViolationError(ClearCraftError):
    """Raised when change ratio exceeds maximum allowed."""

    def __init__(
        self,
        change_ratio: float,
        max_ratio: float,
        message: str = "Change ratio violation",
    ):
        self.change_ratio = change_ratio
        self.max_ratio = max_ratio
        super().__init__(
            f"{message}: {change_ratio:.3f} > {max_ratio:.3f} (max allowed)"
        )


class DisallowedIntentError(ClearCraftError):
    """Raised when disallowed intent keywords are detected."""

    def __init__(
        self,
        keyword: str,
        message: str = "Disallowed intent detected",
    ):
        self.keyword = keyword
        super().__init__(
            f"{message}: '{keyword}' - ClearCraft does not support bypassing AI detectors."
        )


class ChunkingError(ClearCraftError):
    """Raised when text chunking fails."""

    pass


class AnalysisError(ClearCraftError):
    """Raised when text analysis fails."""

    pass


class RewriteError(ClearCraftError):
    """Raised when text rewriting fails."""

    pass


class DeepInfraError(ClearCraftError):
    """Raised when DeepInfra API call fails."""

    pass


class ConfigurationError(ClearCraftError):
    """Raised when configuration is invalid."""

    pass


class TextTooLongError(ClearCraftError):
    """Raised when input text exceeds maximum length."""

    def __init__(self, length: int, max_length: int):
        self.length = length
        self.max_length = max_length
        super().__init__(
            f"Text too long: {length} characters > {max_length} (max allowed)"
        )
