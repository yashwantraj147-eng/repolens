"""Unit tests for multi-model LLM providers (Gemini, Groq, Ollama, OpenAI, and Local)."""

import pytest
import respx
import httpx

from app.config import Settings
from app.services.llm import (
    create_llm_provider,
    GeminiProvider,
    GroqProvider,
    OllamaProvider,
    OpenAIProvider,
    LocalProvider,
)


class TestLLMFactory:
    """Tests for LLM factory provider resolution."""

    def test_default_falls_back_to_local(self) -> None:
        settings = Settings(openai_api_key=None, gemini_api_key=None, groq_api_key=None)
        provider = create_llm_provider(settings)
        assert isinstance(provider, LocalProvider)

    def test_prefers_gemini_when_configured(self) -> None:
        settings = Settings(gemini_api_key="test-gemini-key")
        provider = create_llm_provider(settings)
        assert isinstance(provider, GeminiProvider)
        assert provider.model == "gemini-1.5-flash"

    def test_selects_openai_when_configured(self) -> None:
        settings = Settings(gemini_api_key=None, openai_api_key="test-openai-key")
        provider = create_llm_provider(settings)
        assert isinstance(provider, OpenAIProvider)

    def test_selects_groq_when_configured(self) -> None:
        settings = Settings(
            gemini_api_key=None,
            openai_api_key=None,
            groq_api_key="test-groq-key",
            llm_provider="groq",
        )
        provider = create_llm_provider(settings)
        assert isinstance(provider, GroqProvider)

    def test_explicit_ollama_choice(self) -> None:
        settings = Settings(llm_provider="ollama")
        provider = create_llm_provider(settings)
        assert isinstance(provider, OllamaProvider)


class TestGeminiProvider:
    """Tests for Google Gemini LLM provider."""

    @pytest.mark.asyncio
    async def test_gemini_is_available(self) -> None:
        provider = GeminiProvider(api_key="valid-key-123")
        assert await provider.is_available() is True

        empty_provider = GeminiProvider(api_key="")
        assert await empty_provider.is_available() is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_gemini_generate_success(self) -> None:
        provider = GeminiProvider(api_key="test-key", model="gemini-1.5-flash")
        
        mock_response = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "RepoLens is an open-source GitHub intelligence tool."}
                        ]
                    }
                }
            ]
        }
        respx.post("https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=test-key").respond(
            200, json=mock_response
        )

        result = await provider.generate("Summarize this repo")
        assert "open-source GitHub intelligence tool" in result


class TestGroqProvider:
    """Tests for Groq LLM provider."""

    @pytest.mark.asyncio
    async def test_groq_is_available(self) -> None:
        provider = GroqProvider(api_key="gsk-valid-key")
        assert await provider.is_available() is True

        empty_provider = GroqProvider(api_key="")
        assert await empty_provider.is_available() is False

    @pytest.mark.asyncio
    @respx.mock
    async def test_groq_generate_success(self) -> None:
        provider = GroqProvider(api_key="gsk-test")
        
        mock_response = {
            "choices": [
                {
                    "message": {
                        "content": "Ultra-fast summary from LLaMA 3.3 via Groq."
                    }
                }
            ]
        }
        respx.post("https://api.groq.com/openai/v1/chat/completions").respond(
            200, json=mock_response
        )

        result = await provider.generate("Summarize repository")
        assert "LLaMA 3.3 via Groq" in result


class TestOllamaProvider:
    """Tests for Ollama local provider."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_ollama_is_available(self) -> None:
        provider = OllamaProvider(base_url="http://localhost:11434")
        
        respx.get("http://localhost:11434/api/tags").respond(200, json={"models": []})
        assert await provider.is_available() is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_ollama_generate_success(self) -> None:
        provider = OllamaProvider(base_url="http://localhost:11434", model="llama3")
        
        respx.post("http://localhost:11434/api/generate").respond(
            200, json={"response": "Local Ollama summary for air-gapped security."}
        )

        result = await provider.generate("Summarize repo")
        assert "Local Ollama summary" in result
