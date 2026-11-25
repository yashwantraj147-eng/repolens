"""LLM Provider factory with automatic fallback resolution."""

import logging

from app.config import Settings
from app.services.llm.base import LLMProvider
from app.services.llm.gemini import GeminiProvider
from app.services.llm.groq import GroqProvider
from app.services.llm.local import LocalProvider
from app.services.llm.ollama import OllamaProvider
from app.services.llm.openai import OpenAIProvider

logger = logging.getLogger(__name__)


def create_llm_provider(settings: Settings) -> LLMProvider:
    """Instantiate the configured or best available LLM provider.

    Resolution order when provider is 'auto':
    1. Gemini (if gemini_api_key set)
    2. OpenAI (if openai_api_key set)
    3. Groq (if groq_api_key set)
    4. Local heuristic fallback template (LocalProvider)

    Args:
        settings: Application settings.

    Returns:
        LLMProvider instance.
    """
    choice = (settings.llm_provider or "auto").lower()

    if choice == "gemini" and settings.gemini_api_key:
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    if choice == "groq" and settings.groq_api_key:
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )

    if choice == "openai" and settings.openai_api_key:
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or "https://api.openai.com/v1",
            model=settings.llm_model,
        )

    if choice == "ollama":
        return OllamaProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
        )

    if choice == "local":
        return LocalProvider()

    # 'auto' mode: check available API keys in order
    if settings.gemini_api_key:
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    if settings.openai_api_key:
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or "https://api.openai.com/v1",
            model=settings.llm_model,
        )

    if settings.groq_api_key:
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
        )

    # Default to LocalProvider
    return LocalProvider()
