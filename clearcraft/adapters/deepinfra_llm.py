"""
DeepInfra LLM adapter with ethical guardrails.

Uses DeepInfra's OpenAI-compatible API for optional text polishing.
Includes hard-fail checks for disallowed intents.
"""

import warnings
from typing import Optional, Dict, Any
from openai import OpenAI
from clearcraft.config import settings
from clearcraft.exceptions import DeepInfraError, DisallowedIntentError


class DeepInfraAdapter:
    """Adapter for DeepInfra LLM API with safety guards."""

    # Available models (current as of 2025)
    AVAILABLE_MODELS = [
        "meta-llama/Llama-4-Maverick-17B",
        "meta-llama/Llama-3.3-70B-Instruct",
        "anthropic/claude-3-7-sonnet",
        "anthropic/claude-4-opus",
        "Qwen/Qwen3-235B-Instruct",
        "Qwen/Qwen3-30B-Instruct",
        "Qwen/Qwen3-Coder-480B-A35B-Instruct",
        "microsoft/deepseek-v2",
    ]

    SYSTEM_PROMPT_TEMPLATE = """You are an expert editor focused on improving text clarity, flow, and authentic human tone.

Your role:
- Enhance readability and coherence
- Preserve original meaning exactly
- Maintain all citations, links, and formatting
- Use natural, authentic language

Critical constraints:
- Do NOT attempt to bypass AI detectors
- Do NOT try to make text "undetectable"
- Do NOT alter facts or add information
- Preserve all citations and references exactly

Tone: {tone}
Max changes allowed: {max_change_ratio:.0%}

Focus on genuine clarity improvements only."""

    USER_PROMPT_TEMPLATE = """Please improve the following text for clarity and flow.

Preserve:
- All citations and references
- Technical terms when necessary
- Original meaning and facts
- Paragraph structure

Text to improve:

{text}

Provide only the improved text without explanations or meta-commentary."""

    def __init__(
        self,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize DeepInfra adapter.

        Args:
            api_token: DeepInfra API token. Uses settings if None.
            model: Model ID. Uses settings if None.
            base_url: API base URL. Uses settings if None.

        Raises:
            DeepInfraError: If API token not configured.
        """
        self.api_token = api_token or settings.deepinfra_api_token
        self.model = model or settings.deepinfra_model
        self.base_url = base_url or settings.deepinfra_base_url

        if not self.api_token:
            raise DeepInfraError(
                "DeepInfra API token not configured. "
                "Set DEEPINFRA_API_TOKEN environment variable."
            )

        # Initialize OpenAI client with DeepInfra endpoint
        try:
            self.client = OpenAI(
                api_key=self.api_token,
                base_url=self.base_url,
            )
        except Exception as e:
            raise DeepInfraError(f"Failed to initialize DeepInfra client: {str(e)}") from e

    def check_disallowed_intent(self, text: str) -> None:
        """
        Check for disallowed intent keywords.

        Args:
            text: Text to check.

        Raises:
            DisallowedIntentError: If disallowed keywords found.
        """
        text_lower = text.lower()

        for keyword in settings.disallowed_keywords:
            if keyword.lower() in text_lower:
                raise DisallowedIntentError(
                    keyword=keyword,
                    message="ClearCraft does not support bypassing AI detectors",
                )

    def polish_text(
        self,
        text: str,
        tone: str = "neutral",
        max_change_ratio: float = 0.30,
        similarity_min: float = 0.92,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Polish text using DeepInfra LLM.

        Args:
            text: Text to polish.
            tone: Desired tone (neutral/academic/conversational).
            max_change_ratio: Maximum change ratio.
            similarity_min: Minimum similarity threshold.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Returns:
            Polished text.

        Raises:
            DisallowedIntentError: If disallowed intent detected.
            DeepInfraError: If API call fails.
        """
        # Check for disallowed intent
        self.check_disallowed_intent(text)

        # Prepare prompts
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            tone=tone,
            max_change_ratio=max_change_ratio,
        )

        user_prompt = self.USER_PROMPT_TEMPLATE.format(text=text)

        # Estimate max tokens if not provided
        if max_tokens is None:
            input_tokens = len(text.split()) * 1.3  # Rough estimate
            max_tokens = int(input_tokens * 1.2)  # Allow 20% expansion

        try:
            # Call DeepInfra API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract result
            if not response.choices:
                raise DeepInfraError("No response from DeepInfra API")

            polished_text = response.choices[0].message.content

            if not polished_text:
                raise DeepInfraError("Empty response from DeepInfra API")

            # Re-check for disallowed content in output
            self.check_disallowed_intent(polished_text)

            return polished_text.strip()

        except DisallowedIntentError:
            raise
        except Exception as e:
            raise DeepInfraError(f"DeepInfra API call failed: {str(e)}") from e

    def get_available_models(self) -> list[str]:
        """
        Get list of available models.

        Returns:
            List of model IDs.
        """
        return self.AVAILABLE_MODELS

    def test_connection(self) -> bool:
        """
        Test connection to DeepInfra API.

        Returns:
            True if connection successful.
        """
        try:
            # Simple test call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Test"},
                ],
                max_tokens=10,
            )
            return response is not None
        except Exception as e:
            warnings.warn(f"DeepInfra connection test failed: {e}")
            return False
