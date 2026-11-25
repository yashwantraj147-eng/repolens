"""Router for head-to-head repository comparisons."""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AnalyzeRequest,
    CompareRequest,
    CompareResponse,
    ErrorResponse,
)
from app.routers.analyze import analyze_repo
from app.services.comparison_engine import ComparisonEngine

logger = logging.getLogger(__name__)

router = APIRouter(tags=["compare"])


@router.post(
    "/api/compare",
    response_model=CompareResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid repository URL"},
        404: {"model": ErrorResponse, "description": "Repository not found"},
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Compare two repositories side-by-side",
    description="Analyzes two repositories concurrently and computes head-to-head metrics, category deltas, and synthesis verdict.",
)
async def compare_repositories(request: CompareRequest) -> CompareResponse:
    """Compare two repositories head-to-head.

    Args:
        request: CompareRequest containing repo_a, repo_b URLs and force_refresh.

    Returns:
        CompareResponse with both reports and comparative metrics.
    """
    try:
        # Concurrently analyze both repositories
        req_a = AnalyzeRequest(repo_url=request.repo_a, force_refresh=request.force_refresh)
        req_b = AnalyzeRequest(repo_url=request.repo_b, force_refresh=request.force_refresh)

        report_a, report_b = await asyncio.gather(
            analyze_repo(req_a),
            analyze_repo(req_b),
        )

        comparison = ComparisonEngine().compare(report_a, report_b)

        return CompareResponse(
            repo_a=report_a,
            repo_b=report_b,
            comparison=comparison,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error comparing repositories %s vs %s: %s", request.repo_a, request.repo_b, str(e))
        raise HTTPException(status_code=500, detail=f"Failed to compare repositories: {e!s}") from e
