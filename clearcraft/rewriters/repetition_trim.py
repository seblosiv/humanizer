"""
Repetition trimming and variation.

Removes stock fillers and varies repetitive sentence openings.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import yaml
from pathlib import Path
import random


@dataclass
class RepetitionEdit:
    """Record of a repetition edit."""

    original: str
    edited: str
    edit_type: str  # 'filler_removal', 'opening_variation'
    confidence: float


class RepetitionTrimmer:
    """Trims repetitive phrases and varies sentence openings."""

    def __init__(self, fillers_path: Optional[str] = None, language: str = "en"):
        """
        Initialize repetition trimmer.

        Args:
            fillers_path: Path to fillers YAML file.
            language: Language code (default: "en").
        """
        self.language = language
        self.fillers: List[str] = []
        self.discourse_markers: Dict[str, List[str]] = {}

        # Load fillers and discourse markers
        if fillers_path:
            self._load_fillers(fillers_path)
        else:
            # Try default path
            default_path = Path(__file__).parent.parent.parent / "rules" / f"fillers_{language}.yaml"
            if default_path.exists():
                self._load_fillers(str(default_path))

    def _load_fillers(self, path: str) -> None:
        """
        Load fillers from YAML file.

        Args:
            path: Path to YAML file.
        """
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                self.fillers = data.get("fillers", [])
                self.discourse_markers = data.get("discourse_markers", {})
        except Exception as e:
            print(f"Warning: Failed to load fillers from {path}: {e}")
            self.fillers = []
            self.discourse_markers = {}

    def remove_fillers(self, text: str) -> Tuple[str, List[RepetitionEdit]]:
        """
        Remove stock filler phrases.

        Args:
            text: Input text.

        Returns:
            Tuple of (text_without_fillers, edits).
        """
        edits: List[RepetitionEdit] = []
        result = text

        for filler in self.fillers:
            # Case-insensitive pattern
            pattern = re.compile(r'\b' + re.escape(filler) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(result))

            if matches:
                for match in reversed(matches):  # Reverse to maintain positions
                    edits.append(
                        RepetitionEdit(
                            original=match.group(0),
                            edited="",
                            edit_type="filler_removal",
                            confidence=0.90,
                        )
                    )

                result = pattern.sub("", result)

        # Clean up extra whitespace
        result = re.sub(r"\s+", " ", result)
        result = re.sub(r"\s+([.,!?])", r"\1", result)

        return result, edits

    def vary_openings(self, text: str) -> Tuple[str, List[RepetitionEdit]]:
        """
        Vary repetitive sentence openings.

        Args:
            text: Input text.

        Returns:
            Tuple of (text_with_varied_openings, edits).
        """
        sentences = self._split_sentences(text)
        edits: List[RepetitionEdit] = []
        result_sentences: List[str] = []

        # Track openings
        openings: Dict[str, int] = {}

        for sentence in sentences:
            # Get first few words
            words = sentence.split()
            if len(words) >= 2:
                opening = f"{words[0]} {words[1]}".lower()

                if opening in openings and openings[opening] >= 1:
                    # Try to vary
                    varied = self._vary_opening(sentence)
                    if varied != sentence:
                        edits.append(
                            RepetitionEdit(
                                original=sentence,
                                edited=varied,
                                edit_type="opening_variation",
                                confidence=0.75,
                            )
                        )
                        result_sentences.append(varied)
                    else:
                        result_sentences.append(sentence)
                else:
                    openings[opening] = openings.get(opening, 0) + 1
                    result_sentences.append(sentence)
            else:
                result_sentences.append(sentence)

        result = " ".join(result_sentences)
        return result, edits

    def _vary_opening(self, sentence: str) -> str:
        """
        Attempt to vary sentence opening.

        Args:
            sentence: Input sentence.

        Returns:
            Sentence with varied opening, or original if no variation possible.
        """
        words = sentence.split()
        first_word = words[0].lower() if words else ""

        # Check for discourse markers
        for marker, alternatives in self.discourse_markers.items():
            if first_word == marker.lower() and alternatives:
                # Use a different alternative
                alternative = random.choice(alternatives)
                varied = alternative + " " + " ".join(words[1:])
                return varied

        # If no discourse marker, try to add one
        if first_word not in ["however", "moreover", "furthermore", "additionally"]:
            # Small chance to add a discourse marker
            if random.random() < 0.3:
                markers = ["Furthermore,", "Additionally,", "Moreover,"]
                marker = random.choice(markers)
                return f"{marker} {sentence.lower()}"

        return sentence

    def process(self, text: str) -> Tuple[str, List[RepetitionEdit]]:
        """
        Process text: remove fillers and vary openings.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, edits).
        """
        # Remove fillers first
        text, filler_edits = self.remove_fillers(text)

        # Vary openings
        text, opening_edits = self.vary_openings(text)

        all_edits = filler_edits + opening_edits

        return text, all_edits

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text.

        Returns:
            List of sentences.
        """
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in sentences if s.strip()]
