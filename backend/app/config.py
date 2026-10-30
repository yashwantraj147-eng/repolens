"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # GitHub API
    github_token: Optional[str] = Field(default=None, description="GitHub PAT for higher rate limits")
    github_api_base: str = Field(default="https://api.github.com", description="GitHub API base URL")

    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key for AI summaries")
    openai_base_url: Optional[str] = Field(default=None, description="Custom OpenAI-compatible endpoint")
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM model name")

    # Server
    backend_port: int = Field(default=8000, description="Backend server port")
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173", description="Allowed CORS origins comma-separated")

    # Cache (in-memory by default; configure Redis in production clusters)
    cache_ttl_seconds: int = Field(default=3600, description="Report cache TTL in seconds")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
