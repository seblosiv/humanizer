"""
Grammar correction using language_tool_python.

Applies whitelisted grammar corrections only.
"""

import warnings
from dataclasses import dataclass
from typing import List, Tuple, Set

try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    warnings.warn("language_tool_python not available, grammar checking disabled")


@dataclass
class GrammarCorrection:
    """Record of a grammar correction."""

    original: str
    corrected: str
    rule_id: str
    message: str
    confidence: float


class GrammarCorrector:
    """Applies grammar corrections."""

    # Whitelisted rule categories
    WHITELISTED_CATEGORIES = {
        "GRAMMAR",
        "TYPOS",
        "PUNCTUATION",
        "CAPITALIZATION",
        "CONFUSED_WORDS",
    }

    # Blacklisted rule IDs (too aggressive or style-focused)
    BLACKLISTED_RULES = {
        "WHITESPACE_RULE",
        "DOUBLE_PUNCTUATION",
        "EN_QUOTES",  # Quote style is subjective
    }

    def __init__(self, language: str = "en-US"):
        """
        Initialize grammar corrector.

        Args:
            language: Language code (default: "en-US").
        """
        self.language = language
        self.tool = None

        if LANGUAGE_TOOL_AVAILABLE:
            try:
                self.tool = language_tool_python.LanguageTool(language)
            except Exception as e:
                warnings.warn(f"Failed to initialize LanguageTool: {e}")
                self.tool = None

    def correct(self, text: str) -> Tuple[str, List[GrammarCorrection]]:
        """
        Apply grammar corrections to text.

        Args:
            text: Input text.

        Returns:
            Tuple of (corrected_text, corrections).
        """
        if not self.tool:
            return text, []

        corrections: List[GrammarCorrection] = []

        try:
            # Get matches
            matches = self.tool.check(text)

            # Filter to whitelisted categories
            filtered_matches = [
                match for match in matches
                if self._is_whitelisted(match)
            ]

            # Apply corrections
            corrected = text
            offset = 0

            for match in filtered_matches:
                if match.replacements:
                    # Use first suggested replacement
                    replacement = match.replacements[0]

                    # Calculate positions with offset
                    start = match.offset + offset
                    end = start + match.errorLength

                    # Extract original text
                    original_text = corrected[start:end]

                    # Apply correction
                    corrected = corrected[:start] + replacement + corrected[end:]

                    # Update offset
                    offset += len(replacement) - match.errorLength

                    # Record correction
                    corrections.append(
                        GrammarCorrection(
                            original=original_text,
                            corrected=replacement,
                            rule_id=match.ruleId,
                            message=match.message,
                            confidence=0.85,
                        )
                    )

            return corrected, corrections

        except Exception as e:
            warnings.warn(f"Grammar correction failed: {e}")
            return text, []

    def _is_whitelisted(self, match: any) -> bool:
        """
        Check if a match is whitelisted.

        Args:
            match: LanguageTool match.

        Returns:
            True if whitelisted.
        """
        # Check blacklist first
        if match.ruleId in self.BLACKLISTED_RULES:
            return False

        # Check category whitelist
        category = match.category.upper() if hasattr(match, 'category') else ""

        return category in self.WHITELISTED_CATEGORIES

    def process(self, text: str) -> Tuple[str, List[GrammarCorrection]]:
        """
        Process text and apply grammar corrections.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, corrections).
        """
        return self.correct(text)

    def __del__(self) -> None:
        """Clean up LanguageTool instance."""
        if self.tool:
            try:
                self.tool.close()
            except Exception:
                pass
