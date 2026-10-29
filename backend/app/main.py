"""FastAPI application factory and entry point for RepoLens."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analyze, health, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events.

    Args:
        app: The FastAPI application instance.

    Yields:
        None during the application's lifetime.
    """
    settings = get_settings()
    logger.info("RepoLens starting up on port %d", settings.backend_port)

    if settings.github_token:
        logger.info("GitHub token configured — using authenticated requests (5000 req/hr)")
    else:
        logger.warning("No GITHUB_TOKEN set — limited to 60 requests/hr")

    if settings.openai_api_key:
        logger.info("OpenAI API key configured — AI summaries enabled")
    else:
        logger.info("No OPENAI_API_KEY — using template-based summaries")

    yield

    logger.info("RepoLens shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="RepoLens",
        description=(
            "Analyze any public GitHub repository to get a plain-English summary, "
            "architecture diagram, onboarding guide, and health score."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Configure CORS
    origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router)
    app.include_router(analyze.router)
    app.include_router(reports.router)

    return app


# Application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True,
    )
