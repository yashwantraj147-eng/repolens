"""Groq LLM provider for ultra-low latency inference."""

import logging

import httpx

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """LLM provider powered by Groq's high-speed inference engine."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
    ) -> None:
        """Initialize the Groq provider.

        Args:
            api_key: Groq API key.
            model: Model name (default: 'llama-3.3-70b-versatile').
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using Groq's API.

        Args:
            prompt: Input text prompt.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text content.
        """
        async with httpx.AsyncClient(timeout=20.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": max_tokens,
                        "temperature": 0.7,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except httpx.HTTPStatusError as e:
                logger.error("Groq API error: %s", e.response.text)
                raise RuntimeError(f"Groq API request failed: {e.response.status_code}") from e
            except Exception as e:
                logger.error("Groq provider error: %s", str(e))
                raise RuntimeError(f"Groq generation failed: {e!s}") from e

    async def is_available(self) -> bool:
        """Check if Groq API key is present."""
        return bool(self.api_key and len(self.api_key.strip()) > 5)
