"""
Text formatting normalization.

Normalizes quotes, dashes, spaces, and other formatting elements.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class FormattingEdit:
    """Record of a formatting edit."""

    original: str
    normalized: str
    edit_type: str
    confidence: float


class FormattingNormalizer:
    """Normalizes text formatting."""

    def __init__(self):
        """Initialize formatter."""
        pass

    def normalize_quotes(self, text: str) -> Tuple[str, List[FormattingEdit]]:
        """
        Normalize quotation marks to straight quotes.

        Args:
            text: Input text.

        Returns:
            Tuple of (normalized_text, edits).
        """
        edits: List[FormattingEdit] = []

        # Smart quotes to straight quotes
        replacements = [
            (""", '"', "opening_curly_quote"),
            (""", '"', "closing_curly_quote"),
            ("'", "'", "opening_single_quote"),
            ("'", "'", "closing_single_quote"),
            ("‹", "'", "single_left_angle_quote"),
            ("›", "'", "single_right_angle_quote"),
            ("«", '"', "left_double_angle_quote"),
            ("»", '"', "right_double_angle_quote"),
        ]

        result = text
        for original, replacement, edit_type in replacements:
            if original in result:
                count = result.count(original)
                result = result.replace(original, replacement)
                for _ in range(count):
                    edits.append(
                        FormattingEdit(
                            original=original,
                            normalized=replacement,
                            edit_type=edit_type,
                            confidence=1.0,
                        )
                    )

        return result, edits

    def normalize_dashes(self, text: str) -> Tuple[str, List[FormattingEdit]]:
        """
        Normalize dashes.

        Args:
            text: Input text.

        Returns:
            Tuple of (normalized_text, edits).
        """
        edits: List[FormattingEdit] = []

        # Em dash normalization (—) -> ( — ) with spaces
        em_dash_pattern = re.compile(r"(\w)—(\w)")
        matches = list(em_dash_pattern.finditer(text))
        for match in reversed(matches):
            edits.append(
                FormattingEdit(
                    original="—",
                    normalized=" — ",
                    edit_type="em_dash_spacing",
                    confidence=0.95,
                )
            )
        result = em_dash_pattern.sub(r"\1 — \2", text)

        # En dash (–) in ranges
        result = result.replace("–", "-")

        return result, edits

    def normalize_spaces(self, text: str) -> Tuple[str, List[FormattingEdit]]:
        """
        Normalize spacing.

        Args:
            text: Input text.

        Returns:
            Tuple of (normalized_text, edits).
        """
        edits: List[FormattingEdit] = []

        # Multiple spaces to single space
        multi_space = re.compile(r"  +")
        matches = list(multi_space.finditer(text))
        if matches:
            edits.append(
                FormattingEdit(
                    original="  ",
                    normalized=" ",
                    edit_type="multiple_spaces",
                    confidence=1.0,
                )
            )
        result = multi_space.sub(" ", text)

        # Space before punctuation
        space_before_punct = re.compile(r"\s+([.,!?;:])")
        matches = list(space_before_punct.finditer(result))
        if matches:
            edits.append(
                FormattingEdit(
                    original=" ,",
                    normalized=",",
                    edit_type="space_before_punctuation",
                    confidence=1.0,
                )
            )
        result = space_before_punct.sub(r"\1", result)

        # No space after punctuation
        no_space_after_punct = re.compile(r"([.,!?;:])([A-Z])")
        matches = list(no_space_after_punct.finditer(result))
        if matches:
            edits.append(
                FormattingEdit(
                    original=".A",
                    normalized=". A",
                    edit_type="missing_space_after_punctuation",
                    confidence=1.0,
                )
            )
        result = no_space_after_punct.sub(r"\1 \2", result)

        return result, edits

    def normalize_ellipsis(self, text: str) -> Tuple[str, List[FormattingEdit]]:
        """
        Normalize ellipsis.

        Args:
            text: Input text.

        Returns:
            Tuple of (normalized_text, edits).
        """
        edits: List[FormattingEdit] = []

        # Multiple dots to proper ellipsis
        ellipsis_pattern = re.compile(r"\.{3,}")
        matches = list(ellipsis_pattern.finditer(text))
        if matches:
            edits.append(
                FormattingEdit(
                    original="....",
                    normalized="...",
                    edit_type="ellipsis_normalization",
                    confidence=1.0,
                )
            )
        result = ellipsis_pattern.sub("...", text)

        return result, edits

    def process(self, text: str) -> Tuple[str, List[FormattingEdit]]:
        """
        Apply all formatting normalizations.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, all_edits).
        """
        all_edits: List[FormattingEdit] = []

        # Apply each normalization
        text, quote_edits = self.normalize_quotes(text)
        all_edits.extend(quote_edits)

        text, dash_edits = self.normalize_dashes(text)
        all_edits.extend(dash_edits)

        text, space_edits = self.normalize_spaces(text)
        all_edits.extend(space_edits)

        text, ellipsis_edits = self.normalize_ellipsis(text)
        all_edits.extend(ellipsis_edits)

        return text, all_edits
