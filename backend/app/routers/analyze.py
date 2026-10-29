"""Analysis endpoint for processing GitHub repositories."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import AnalyzeRequest, AnalysisReport, ErrorResponse
from app.services.github_client import (
    GitHubClient,
    GitHubClientError,
    RateLimitExceededError,
    RepoNotFoundError,
)
from app.utils.validators import parse_github_url

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])

# In-memory report cache (TTL managed at application level)
_report_cache: Dict[str, AnalysisReport] = {}


def get_report_cache() -> Dict[str, AnalysisReport]:
    """Get the in-memory report cache.

    Returns:
        Dictionary mapping report IDs to AnalysisReport objects.
    """
    return _report_cache


@router.post(
    "/api/analyze",
    response_model=AnalysisReport,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
    summary="Analyze a GitHub repository",
    description="Accepts a GitHub repository URL and returns a comprehensive analysis report.",
)
async def analyze_repo(request: AnalyzeRequest) -> AnalysisReport:
    """Analyze a public GitHub repository.

    Fetches repository data from the GitHub API and produces:
    - A plain-English summary
    - An architecture diagram (Mermaid)
    - A contributor onboarding guide
    - A health score (0-100)

    Args:
        request: Request body containing the GitHub repo URL.

    Returns:
        Complete AnalysisReport with all generated content.

    Raises:
        HTTPException: On validation errors, not-found, or rate limits.
    """
    settings = get_settings()

    try:
        owner, repo = parse_github_url(request.repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    client = GitHubClient(settings)

    try:
        # Fetch repository info
        repo_info = await client.get_repo_info(owner, repo)

        # Fetch additional data for analysis
        readme_content = await client.get_readme(owner, repo)
        file_tree = await client.get_file_tree(owner, repo)
        recent_commits = await client.get_recent_commits(owner, repo)
        closed_issues = await client.get_closed_issues(owner, repo)
        languages = await client.get_languages(owner, repo)

        # Import services (lazy to avoid circular imports during startup)
        from app.services.scoring_engine import ScoringEngine
        from app.services.diagram_generator import DiagramGenerator
        from app.services.summary_generator import SummaryGenerator
        from app.services.onboarding_guide import OnboardingGuideGenerator

        # Generate health score
        scoring_engine = ScoringEngine()
        health_score = scoring_engine.calculate_score(
            repo_info=repo_info,
            readme_content=readme_content,
            file_tree=file_tree,
            recent_commits=recent_commits,
            closed_issues=closed_issues,
        )

        # Generate architecture diagram
        diagram_gen = DiagramGenerator()
        architecture_diagram = diagram_gen.generate(
            repo_info=repo_info,
            file_tree=file_tree,
            languages=languages,
        )

        # Generate summary
        summary_gen = SummaryGenerator(settings)
        summary = await summary_gen.generate(
            repo_info=repo_info,
            readme_content=readme_content,
            languages=languages,
            file_tree=file_tree,
        )

        # Generate onboarding guide
        onboarding_gen = OnboardingGuideGenerator(settings)
        onboarding_guide = await onboarding_gen.generate(
            repo_info=repo_info,
            readme_content=readme_content,
            file_tree=file_tree,
            languages=languages,
        )

        # Build report
        report = AnalysisReport(
            report_id=str(uuid.uuid4()),
            repo=repo_info,
            summary=summary,
            architecture_diagram=architecture_diagram,
            onboarding_guide=onboarding_guide,
            health_score=health_score,
            generated_at=datetime.now(timezone.utc),
        )

        # Cache the report
        _report_cache[report.report_id] = report

        logger.info(
            "Analysis complete for %s/%s — Score: %d (%s)",
            owner,
            repo,
            health_score.overall,
            health_score.grade,
        )

        return report

    except RepoNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except GitHubClientError as e:
        logger.error("GitHub API error analyzing %s/%s: %s", owner, repo, str(e))
        raise HTTPException(status_code=502, detail=f"GitHub API error: {str(e)}")
    except Exception as e:
        logger.error("Unexpected error analyzing %s/%s: %s", owner, repo, str(e))
        raise HTTPException(status_code=500, detail="An unexpected error occurred during analysis.")
