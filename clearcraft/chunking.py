"""
Markdown/HTML-aware text chunking with protected spans.

Segments text while preserving:
- Code blocks (fenced and indented)
- Links and citations
- Block quotes
- Footnotes
- HTML tags
"""

import re
from dataclasses import dataclass
from typing import List, Tuple
from clearcraft.exceptions import ChunkingError


@dataclass
class ProtectedSpan:
    """A span of text that should not be modified."""

    start: int
    end: int
    content: str
    span_type: str  # 'code', 'link', 'quote', 'footnote', 'html'


@dataclass
class TextChunk:
    """A chunk of text with metadata."""

    text: str
    start: int
    end: int
    protected_spans: List[ProtectedSpan]


class TextChunker:
    """Chunks text while preserving special formatting."""

    # Regex patterns for protected content
    PATTERNS = {
        "fenced_code": re.compile(r"```[\s\S]*?```|~~~[\s\S]*?~~~", re.MULTILINE),
        "indented_code": re.compile(r"(?:^|\n)(?: {4}|\t).+(?:\n(?: {4}|\t).+)*", re.MULTILINE),
        "inline_code": re.compile(r"`[^`]+`"),
        "links": re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
        "reference_links": re.compile(r"\[([^\]]+)\]\[([^\]]*)\]"),
        "footnotes": re.compile(r"\[\^[^\]]+\]"),
        "blockquote": re.compile(r"(?:^|\n)>.*(?:\n>.*)*", re.MULTILINE),
        "html_tags": re.compile(r"<[^>]+>"),
        "citations": re.compile(r"\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s+\d{4}\)"),
    }

    def __init__(self, chunk_size: int = 1000):
        """
        Initialize chunker.

        Args:
            chunk_size: Target size for chunks in characters.
        """
        self.chunk_size = chunk_size

    def find_protected_spans(self, text: str) -> List[ProtectedSpan]:
        """
        Find all protected spans in text.

        Args:
            text: Input text.

        Returns:
            List of protected spans.
        """
        protected_spans: List[ProtectedSpan] = []

        for span_type, pattern in self.PATTERNS.items():
            for match in pattern.finditer(text):
                protected_spans.append(
                    ProtectedSpan(
                        start=match.start(),
                        end=match.end(),
                        content=match.group(0),
                        span_type=span_type,
                    )
                )

        # Sort by start position
        protected_spans.sort(key=lambda x: x.start)

        # Merge overlapping spans
        merged: List[ProtectedSpan] = []
        for span in protected_spans:
            if merged and span.start < merged[-1].end:
                # Overlapping - extend the previous span
                last = merged[-1]
                merged[-1] = ProtectedSpan(
                    start=last.start,
                    end=max(last.end, span.end),
                    content=text[last.start : max(last.end, span.end)],
                    span_type=f"{last.span_type}+{span.span_type}",
                )
            else:
                merged.append(span)

        return merged

    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        Chunk text while respecting protected spans.

        Args:
            text: Input text.

        Returns:
            List of text chunks.

        Raises:
            ChunkingError: If chunking fails.
        """
        try:
            if not text or not text.strip():
                return []

            protected_spans = self.find_protected_spans(text)
            chunks: List[TextChunk] = []

            # Split text at paragraph boundaries
            paragraphs = re.split(r"\n\n+", text)
            current_chunk = ""
            current_start = 0

            for para in paragraphs:
                para_start = text.find(para, current_start)

                # Check if adding this paragraph would exceed chunk size
                if len(current_chunk) + len(para) + 2 > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunk_end = para_start
                    chunk_protected = [
                        s for s in protected_spans
                        if s.start >= current_start and s.end <= chunk_end
                    ]
                    chunks.append(
                        TextChunk(
                            text=current_chunk.strip(),
                            start=current_start,
                            end=chunk_end,
                            protected_spans=chunk_protected,
                        )
                    )
                    current_chunk = para
                    current_start = para_start
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                        current_start = para_start

            # Add final chunk
            if current_chunk:
                chunk_protected = [
                    s for s in protected_spans
                    if s.start >= current_start
                ]
                chunks.append(
                    TextChunk(
                        text=current_chunk.strip(),
                        start=current_start,
                        end=len(text),
                        protected_spans=chunk_protected,
                    )
                )

            return chunks

        except Exception as e:
            raise ChunkingError(f"Failed to chunk text: {str(e)}") from e

    def is_protected(self, position: int, protected_spans: List[ProtectedSpan]) -> bool:
        """
        Check if a position is within a protected span.

        Args:
            position: Character position.
            protected_spans: List of protected spans.

        Returns:
            True if position is protected.
        """
        return any(span.start <= position < span.end for span in protected_spans)

    def get_safe_split_positions(
        self,
        text: str,
        protected_spans: List[ProtectedSpan],
    ) -> List[int]:
        """
        Get positions where text can be safely split.

        Args:
            text: Input text.
            protected_spans: List of protected spans.

        Returns:
            List of safe split positions.
        """
        # Find sentence boundaries (., !, ?)
        sentence_ends = [m.end() for m in re.finditer(r"[.!?]\s+", text)]

        # Filter to only unprotected positions
        safe_positions = [
            pos for pos in sentence_ends
            if not self.is_protected(pos, protected_spans)
        ]

        return safe_positions
