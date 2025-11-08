"""
ClearCraft - Production-grade text clarity and readability enhancement tool.

A Python toolkit for improving text readability, coherence, and style while
preserving meaning, citations, and formatting. Features ethical guardrails
to ensure semantic similarity and prevent misuse.
"""

__version__ = "1.0.0"
__author__ = "ClearCraft Team"

from clearcraft.config import Settings
from clearcraft.exceptions import (
    ClearCraftError,
    SimilarityViolationError,
    ChangeRatioViolationError,
    DisallowedIntentError,
)

__all__ = [
    "Settings",
    "ClearCraftError",
    "SimilarityViolationError",
    "ChangeRatioViolationError",
    "DisallowedIntentError",
]
