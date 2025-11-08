"""
Configuration management for ClearCraft using Pydantic Settings.

Loads configuration from environment variables with sensible defaults.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")

    # DeepInfra API (Optional)
    deepinfra_api_token: Optional[str] = Field(
        default=None,
        description="DeepInfra API token (optional - leave empty to disable LLM pass)",
    )
    deepinfra_model: str = Field(
        default="meta-llama/Llama-4-Maverick-17B",
        description="DeepInfra model ID",
    )
    deepinfra_base_url: str = Field(
        default="https://api.deepinfra.com/v1/openai",
        description="DeepInfra OpenAI-compatible API base URL",
    )

    # Processing Limits
    max_text_length: int = Field(
        default=50000,
        description="Maximum text length in characters",
    )
    chunk_size: int = Field(
        default=1000,
        description="Chunk size for processing",
    )

    # Quality Guardrails
    max_change_ratio: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Maximum allowed change ratio (0.0-1.0)",
    )
    similarity_min: float = Field(
        default=0.92,
        ge=0.0,
        le=1.0,
        description="Minimum semantic similarity threshold (0.0-1.0)",
    )
    preserve_citations: bool = Field(
        default=True,
        description="Preserve citations, links, and footnotes",
    )

    # Readability Targets
    target_avg_sentence_length_min: int = Field(
        default=14,
        ge=5,
        description="Minimum target average sentence length in tokens",
    )
    target_avg_sentence_length_max: int = Field(
        default=22,
        ge=10,
        description="Maximum target average sentence length in tokens",
    )
    max_passive_ratio: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="Maximum passive voice ratio (0.0-1.0)",
    )
    max_repetition_ratio: float = Field(
        default=0.10,
        ge=0.0,
        le=1.0,
        description="Maximum repetition ratio (0.0-1.0)",
    )

    # Model Cache
    transformers_cache: str = Field(
        default=".cache/huggingface",
        description="Transformers model cache directory",
    )
    sentence_transformers_home: str = Field(
        default=".cache/sentence-transformers",
        description="Sentence transformers cache directory",
    )

    # Sentence Transformer Model
    sentence_transformer_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Sentence transformer model for similarity checking",
    )

    # spaCy Model
    spacy_model: str = Field(
        default="en_core_web_sm",
        description="spaCy model for NLP processing",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_file: str = Field(
        default="clearcraft.log",
        description="Log file path",
    )

    # Privacy & Compliance
    enable_disclosure: bool = Field(
        default=True,
        description="Add disclosure message to output",
    )
    redact_pii_in_logs: bool = Field(
        default=True,
        description="Redact PII in log files",
    )

    # Disallowed Intent Keywords (hard-fail)
    disallowed_keywords: list[str] = Field(
        default=[
            "bypass",
            "evade",
            "undetectable",
            "ai detector",
            "fool detector",
            "hide ai",
            "mask ai",
            "defeat detection",
        ],
        description="Keywords that trigger intent violation",
    )

    @property
    def is_deepinfra_enabled(self) -> bool:
        """Check if DeepInfra integration is enabled."""
        return self.deepinfra_api_token is not None and len(self.deepinfra_api_token) > 0

    def get_disclosure_message(self) -> str:
        """Get the disclosure message to append to output."""
        if self.enable_disclosure:
            return "\n\n---\n*Edited with AI assistance.*"
        return ""


# Global settings instance
settings = Settings()
