"""Report retrieval and recent reports endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import AnalysisReport, ErrorResponse, RecentReportItem
from app.services.report_store import get_report_store

router = APIRouter(tags=["reports"])


@router.get(
    "/api/reports/recent",
    response_model=List[RecentReportItem],
    summary="List recently analyzed repositories",
    description="Retrieve a list of the most recently analyzed repositories for display on the landing page.",
)
async def get_recent_reports(
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of items to return"),
) -> List[RecentReportItem]:
    """Retrieve recently analyzed repository summaries.

    Args:
        limit: Maximum number of recent reports to return (1-50).

    Returns:
        List of RecentReportItem objects.
    """
    store = get_report_store()
    return store.get_recent(limit=limit)


@router.get(
    "/api/reports/{report_id}",
    response_model=AnalysisReport,
    responses={
        404: {"model": ErrorResponse, "description": "Report not found"},
    },
    summary="Retrieve a previously generated report",
    description="Fetch an analysis report by its unique ID from persistent storage or cache.",
)
async def get_report(report_id: str) -> AnalysisReport:
    """Retrieve a persistent or cached analysis report by ID.

    Args:
        report_id: The unique report identifier (UUID).

    Returns:
        The persistent AnalysisReport.

    Raises:
        HTTPException: If the report is not found.
    """
    store = get_report_store()
    report = store.get_by_id(report_id)

    # Fallback to in-memory cache if not found in store
    if not report:
        from app.routers.analyze import get_report_cache
        cache = get_report_cache()
        report = cache.get(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_id}' not found. Reports are cached for a limited time.",
        )

    return report
