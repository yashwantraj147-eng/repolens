"""Local Ollama LLM provider."""

import logging
from typing import Optional

import httpx

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """LLM provider connecting to a local Ollama instance."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3",
    ) -> None:
        """Initialize Ollama provider.

        Args:
            base_url: Ollama daemon URL.
            model: Model tag (default: 'llama3').
        """
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text using local Ollama.

        Args:
            prompt: Input text prompt.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text content.
        """
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": 0.7,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
            except Exception as e:
                logger.error("Ollama provider error: %s", str(e))
                raise RuntimeError(f"Ollama generation failed: {str(e)}") from e

    async def is_available(self) -> bool:
        """Check if local Ollama daemon is running."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False
