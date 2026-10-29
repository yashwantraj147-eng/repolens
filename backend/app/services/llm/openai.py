"""OpenAI-compatible LLM provider."""

import logging
from typing import Optional

import httpx

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """LLM provider using OpenAI-compatible API.

    Supports OpenAI, Azure OpenAI, and any compatible endpoint
    (e.g., local LLM servers like Ollama, LM Studio).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-3.5-turbo",
    ) -> None:
        """Initialize the OpenAI provider.

        Args:
            api_key: API key for authentication.
            base_url: Base URL for the OpenAI-compatible API.
            model: Model name to use for completions.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using the OpenAI-compatible API.

        Args:
            prompt: The input prompt.
            max_tokens: Maximum tokens in the response.

        Returns:
            The generated text completion.

        Raises:
            RuntimeError: If the API request fails.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
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
                logger.error("OpenAI API error: %s", e.response.text)
                raise RuntimeError(f"LLM API request failed: {e.response.status_code}") from e
            except Exception as e:
                logger.error("OpenAI provider error: %s", str(e))
                raise RuntimeError(f"LLM generation failed: {str(e)}") from e

    async def is_available(self) -> bool:
        """Check if the OpenAI API is reachable.

        Returns:
            True if the API responds to a models list request.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return response.status_code == 200
        except Exception:
            return False
