"""
Deterministic text rewriters for clarity enhancement.

Each rewriter applies specific transformations while preserving meaning.
"""

from clearcraft.rewriters.syntax_split import SyntaxSplitter
from clearcraft.rewriters.syntax_merge import SyntaxMerger
from clearcraft.rewriters.voice_active import VoiceActivator
from clearcraft.rewriters.jargon_plain import JargonSimplifier
from clearcraft.rewriters.repetition_trim import RepetitionTrimmer
from clearcraft.rewriters.grammar import GrammarCorrector
from clearcraft.rewriters.formatting import FormattingNormalizer

__all__ = [
    "SyntaxSplitter",
    "SyntaxMerger",
    "VoiceActivator",
    "JargonSimplifier",
    "RepetitionTrimmer",
    "GrammarCorrector",
    "FormattingNormalizer",
]
