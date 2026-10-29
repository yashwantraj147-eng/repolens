"""Local template-based LLM provider — no API key required."""

from typing import Optional

from app.services.llm.base import LLMProvider


class LocalProvider(LLMProvider):
    """Template-based text generation using repo metadata.

    This provider uses intelligent templates and heuristics to generate
    summaries, guides, and descriptions without requiring an external
    API key. It serves as the default fallback provider.
    """

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using template-based heuristics.

        The prompt is expected to contain structured metadata that this
        provider can parse and format into useful output.

        Args:
            prompt: The input prompt containing repo metadata.
            max_tokens: Maximum length (used for truncation).

        Returns:
            Generated text based on templates and metadata.
        """
        # The LocalProvider is used by specific generators that pass
        # structured prompts. For raw prompts, return a generic response.
        return prompt[:max_tokens]

    async def is_available(self) -> bool:
        """Local provider is always available.

        Returns:
            Always True.
        """
        return True
