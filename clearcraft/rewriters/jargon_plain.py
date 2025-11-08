"""
Jargon to plain language simplification.

Uses curated YAML lexicons and word frequency analysis to replace
technical jargon with plainer alternatives.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import yaml
from pathlib import Path

try:
    from wordfreq import word_frequency
    WORDFREQ_AVAILABLE = True
except ImportError:
    WORDFREQ_AVAILABLE = False


@dataclass
class JargonReplacement:
    """Record of a jargon replacement."""

    original_word: str
    replacement: str
    confidence: float
    reason: str


class JargonSimplifier:
    """Simplifies jargon to plain language."""

    def __init__(self, lexicon_path: Optional[str] = None, language: str = "en"):
        """
        Initialize jargon simplifier.

        Args:
            lexicon_path: Path to jargon lexicon YAML file.
            language: Language code (default: "en").
        """
        self.language = language
        self.lexicon: Dict[str, Dict[str, any]] = {}

        # Load lexicon
        if lexicon_path:
            self._load_lexicon(lexicon_path)
        else:
            # Try default path
            default_path = Path(__file__).parent.parent.parent / "rules" / f"jargon_{language}.yaml"
            if default_path.exists():
                self._load_lexicon(str(default_path))

    def _load_lexicon(self, path: str) -> None:
        """
        Load jargon lexicon from YAML file.

        Args:
            path: Path to YAML file.
        """
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f)
                self.lexicon = data.get("jargon", {})
        except Exception as e:
            print(f"Warning: Failed to load lexicon from {path}: {e}")
            self.lexicon = {}

    def simplify_word(self, word: str, context: str = "") -> Optional[JargonReplacement]:
        """
        Simplify a jargon word if appropriate.

        Args:
            word: Word to potentially simplify.
            context: Surrounding context for disambiguation.

        Returns:
            JargonReplacement if replacement made, None otherwise.
        """
        word_lower = word.lower()

        # Check lexicon
        if word_lower in self.lexicon:
            entry = self.lexicon[word_lower]
            replacement = entry.get("replacement", "")
            pos = entry.get("pos", "")  # Part of speech

            if replacement:
                # Check word frequency if available
                confidence = 0.75

                if WORDFREQ_AVAILABLE:
                    orig_freq = word_frequency(word_lower, self.language)
                    repl_freq = word_frequency(replacement, self.language)

                    # Replacement should be more common
                    if repl_freq > orig_freq:
                        confidence = 0.85
                    elif repl_freq < orig_freq:
                        confidence = 0.60

                # Preserve capitalization
                if word[0].isupper():
                    replacement = replacement.capitalize()

                return JargonReplacement(
                    original_word=word,
                    replacement=replacement,
                    confidence=confidence,
                    reason=f"jargon_to_plain_{pos}" if pos else "jargon_to_plain",
                )

        return None

    def process(self, text: str) -> Tuple[str, List[JargonReplacement]]:
        """
        Process text and simplify jargon.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, replacements).
        """
        replacements: List[JargonReplacement] = []
        result = text

        # Tokenize while preserving whitespace
        words = re.findall(r"\b\w+\b|\s+|[^\w\s]", text)
        processed_words: List[str] = []

        for i, token in enumerate(words):
            if re.match(r"\b\w+\b", token):
                # Get context (5 words before and after)
                context_start = max(0, i - 5)
                context_end = min(len(words), i + 6)
                context = "".join(words[context_start:context_end])

                replacement = self.simplify_word(token, context)
                if replacement and replacement.confidence >= 0.70:
                    replacements.append(replacement)
                    processed_words.append(replacement.replacement)
                else:
                    processed_words.append(token)
            else:
                processed_words.append(token)

        result = "".join(processed_words)
        return result, replacements
