"""Google Gemini LLM provider using the Google AI REST API."""

import logging

import httpx

from app.services.llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """LLM provider for Google's Gemini models."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
    ) -> None:
        """Initialize the Gemini provider.

        Args:
            api_key: Google Gemini API key.
            model: Gemini model identifier (default: 'gemini-1.5-flash').
        """
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )

    async def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        """Generate text completion from Google Gemini API.

        Args:
            prompt: Input text prompt.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text content.

        Raises:
            RuntimeError: If the API request fails.
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.endpoint}?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "parts": [{"text": prompt}],
                            }
                        ],
                        "generationConfig": {
                            "maxOutputTokens": max_tokens,
                            "temperature": 0.7,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("No generation candidates returned by Gemini API")
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if not parts:
                    raise RuntimeError("No text parts returned in candidate")
                return parts[0].get("text", "")
            except httpx.HTTPStatusError as e:
                logger.error("Gemini API error: %s", e.response.text)
                raise RuntimeError(f"Gemini API request failed: {e.response.status_code}") from e
            except Exception as e:
                logger.error("Gemini provider error: %s", str(e))
                raise RuntimeError(f"Gemini generation failed: {e!s}") from e

    async def is_available(self) -> bool:
        """Check if Gemini API key is configured.

        Returns:
            True if api_key is non-empty.
        """
        return bool(self.api_key and len(self.api_key.strip()) > 5)
