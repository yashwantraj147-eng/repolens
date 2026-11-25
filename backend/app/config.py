"""Application configuration using pydantic-settings."""


from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub API
    github_token: str | None = Field(default=None, description="GitHub PAT for higher rate limits")
    github_api_base: str = Field(default="https://api.github.com", description="GitHub API base URL")

    # LLM Configuration
    llm_provider: str = Field(default="auto", description="LLM provider: auto, openai, gemini, groq, ollama, local")
    openai_api_key: str | None = Field(default=None, description="OpenAI API key for AI summaries")
    openai_base_url: str | None = Field(default=None, description="Custom OpenAI-compatible endpoint")
    llm_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model name")
    gemini_api_key: str | None = Field(default=None, description="Google Gemini API key")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model name")
    groq_api_key: str | None = Field(default=None, description="Groq API key")
    groq_model: str = Field(default="llama-3.3-70b-versatile", description="Groq model name")
    ollama_base_url: str | None = Field(default="http://localhost:11434", description="Local Ollama base URL")
    ollama_model: str = Field(default="llama3", description="Ollama model name")

    # Server
    backend_port: int = Field(default=8000, description="Backend server port")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173", description="Allowed CORS origins comma-separated")

    # Cache & Storage
    cache_ttl_seconds: int = Field(default=3600, description="Report cache TTL in seconds")
    db_path: str = Field(default="repolens.db", description="Path to SQLite database for persistent report storage")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
