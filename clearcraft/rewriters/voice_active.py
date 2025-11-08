"""
Passive to active voice conversion.

Uses pattern matching to identify and convert passive voice constructions.
Includes confidence scoring to avoid incorrect transformations.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class VoiceConversion:
    """Record of a passive-to-active conversion."""

    original: str
    converted: str
    confidence: float
    reason: str


class VoiceActivator:
    """Converts passive voice to active voice."""

    # Passive voice patterns
    PASSIVE_PATTERNS = [
        # Simple passive: "is/was done by X"
        (
            re.compile(r"(is|was|are|were)\s+(\w+ed)\s+by\s+([^.,]+)", re.IGNORECASE),
            r"\3 \2",
            0.80,
            "simple_passive_by",
        ),
        # Passive without agent: "is/was done"
        (
            re.compile(r"(is|was|are|were)\s+(\w+ed)(?!\s+by)", re.IGNORECASE),
            None,  # Requires more context
            0.50,
            "agentless_passive",
        ),
    ]

    def __init__(self):
        """Initialize voice activator."""
        pass

    def detect_passive(self, sentence: str) -> bool:
        """
        Detect if sentence contains passive voice.

        Args:
            sentence: Input sentence.

        Returns:
            True if passive voice detected.
        """
        for pattern, _, _, _ in self.PASSIVE_PATTERNS:
            if pattern.search(sentence):
                return True
        return False

    def convert_to_active(self, sentence: str) -> Optional[VoiceConversion]:
        """
        Convert passive voice to active voice.

        Args:
            sentence: Input sentence in passive voice.

        Returns:
            VoiceConversion if successful, None otherwise.
        """
        # Try simple "by X" passive
        pattern = re.compile(
            r"(.+?)\s+(is|was|are|were)\s+(\w+ed)\s+by\s+([^.,]+)(.*)",
            re.IGNORECASE,
        )
        match = pattern.match(sentence)

        if match:
            subject, aux, verb, agent, rest = match.groups()

            # Convert verb from past participle to simple past/present
            # This is a simplified version - full conversion needs verb conjugation
            active_verb = self._convert_verb(verb, aux)

            # Construct active voice: agent + verb + subject
            converted = f"{agent.strip()} {active_verb} {subject.strip()}{rest}"

            # Capitalize first letter
            converted = converted[0].upper() + converted[1:] if len(converted) > 1 else converted

            return VoiceConversion(
                original=sentence,
                converted=converted,
                confidence=0.75,
                reason="passive_by_agent",
            )

        return None

    def _convert_verb(self, past_participle: str, auxiliary: str) -> str:
        """
        Convert past participle to active form.

        This is a simplified conversion - proper implementation would use
        a verb conjugation library or spaCy.

        Args:
            past_participle: Past participle form (e.g., "written").
            auxiliary: Auxiliary verb (is/was/are/were).

        Returns:
            Active verb form.
        """
        # Common irregular verbs
        irregular = {
            "written": "wrote" if auxiliary in ["was", "were"] else "writes",
            "done": "did" if auxiliary in ["was", "were"] else "does",
            "made": "made" if auxiliary in ["was", "were"] else "makes",
            "taken": "took" if auxiliary in ["was", "were"] else "takes",
            "given": "gave" if auxiliary in ["was", "were"] else "gives",
            "seen": "saw" if auxiliary in ["was", "were"] else "sees",
        }

        if past_participle in irregular:
            return irregular[past_participle]

        # Regular verbs: remove 'ed'
        if past_participle.endswith("ed"):
            base = past_participle[:-2]
            if auxiliary in ["was", "were"]:
                return base + "ed"  # Past tense
            else:
                return base + "s"  # Present tense third person

        return past_participle

    def process(self, text: str) -> Tuple[str, List[VoiceConversion]]:
        """
        Process text and convert passive voice to active.

        Args:
            text: Input text.

        Returns:
            Tuple of (processed_text, conversions).
        """
        sentences = self._split_sentences(text)
        conversions: List[VoiceConversion] = []
        result_sentences: List[str] = []

        for sentence in sentences:
            conversion = self.convert_to_active(sentence)
            if conversion and conversion.confidence >= 0.70:
                conversions.append(conversion)
                result_sentences.append(conversion.converted)
            else:
                result_sentences.append(sentence)

        # Reconstruct text
        processed_text = " ".join(result_sentences)

        return processed_text, conversions

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
