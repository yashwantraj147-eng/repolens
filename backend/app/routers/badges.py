"""Dynamic SVG badge generation router for GitHub repository health."""

import logging

from fastapi import APIRouter, HTTPException, Query, Response

from app.config import get_settings
from app.models.schemas import AnalyzeRequest
from app.services.badge_generator import generate_badge_svg
from app.services.report_store import get_report_store

logger = logging.getLogger(__name__)

router = APIRouter(tags=["badges"])


@router.get(
    "/api/badge/id/{report_id}.svg",
    summary="Get report health score SVG badge by report ID",
    description="Returns a vector SVG badge for a specific report ID.",
    response_class=Response,
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "Dynamic SVG badge image",
        }
    },
)
async def get_badge_by_id(
    report_id: str,
    style: str = Query(default="flat", pattern="^(flat|flat-square|for-the-badge)$"),
) -> Response:
    """Generate SVG badge from a specific report ID."""
    store = get_report_store()
    report = store.get_by_id(report_id)

    if not report:
        svg = generate_badge_svg(label="repolens", value="not found", grade="unknown", style=style)
        return Response(content=svg, media_type="image/svg+xml", headers={"Cache-Control": "public, max-age=60"})

    score = report.health_score.overall
    grade = report.health_score.grade
    svg = generate_badge_svg(
        label="repolens",
        value=f"{score}/100 · {grade}",
        grade=grade,
        style=style,
    )

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=3600", "ETag": f'"{report.report_id}"'},
    )


@router.get(
    "/api/badge/{owner}/{repo}.svg",
    summary="Get repository health score SVG badge",
    description="Returns a Shields.io-compatible vector SVG badge displaying the repository's RepoLens health score.",
    response_class=Response,
    responses={
        200: {
            "content": {"image/svg+xml": {}},
            "description": "Dynamic SVG badge image",
        }
    },
)
async def get_repo_badge(
    owner: str,
    repo: str,
    style: str = Query(default="flat", pattern="^(flat|flat-square|for-the-badge)$", description="Badge visual style"),
    metric: str = Query(default="score", pattern="^(score|grade|percent)$", description="Displayed score format"),
) -> Response:
    """Generate or retrieve a dynamic SVG badge for a repository.

    Args:
        owner: Repository owner/organization.
        repo: Repository name.
        style: Visual style ('flat', 'flat-square', 'for-the-badge').
        metric: Format ('score', 'grade', 'percent').

    Returns:
        Response containing SVG vector markup with caching headers.
    """
    settings = get_settings()
    store = get_report_store(settings.db_path)

    # Check cache first
    report = store.get_latest_for_repo(owner, repo, max_age_seconds=settings.cache_ttl_seconds)

    # If not cached, trigger analysis to generate the report
    if not report:
        try:
            from app.routers.analyze import analyze_repo
            req = AnalyzeRequest(repo_url=f"https://github.com/{owner}/{repo}")
            report = await analyze_repo(req, response=Response())
        except (HTTPException, OSError, ValueError, RuntimeError, TypeError, KeyError) as e:
            logger.warning("Could not auto-generate report for badge %s/%s: %s", owner, repo, str(e))
            svg = generate_badge_svg(
                label="repolens",
                value="not audited",
                grade="unknown",
                style=style,
            )
            return Response(
                content=svg,
                media_type="image/svg+xml",
                headers={"Cache-Control": "public, max-age=300"},
            )

    score = report.health_score.overall
    grade = report.health_score.grade

    if metric == "grade":
        value_text = f"Grade {grade}"
    elif metric == "percent":
        value_text = f"{score}%"
    else:
        value_text = f"{score}/100 · {grade}"

    svg = generate_badge_svg(
        label="repolens",
        value=value_text,
        grade=grade,
        style=style,
    )

    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={
            "Cache-Control": f"public, max-age={settings.cache_ttl_seconds}, s-maxage={settings.cache_ttl_seconds}",
            "ETag": f'"{report.report_id}"',
        },
    )
