"""Report retrieval endpoint."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import AnalysisReport, ErrorResponse

router = APIRouter(tags=["reports"])


@router.get(
    "/api/reports/{report_id}",
    response_model=AnalysisReport,
    responses={
        404: {"model": ErrorResponse, "description": "Report not found"},
    },
    summary="Retrieve a previously generated report",
    description="Fetch an analysis report by its unique ID.",
)
async def get_report(report_id: str) -> AnalysisReport:
    """Retrieve a cached analysis report by ID.

    Args:
        report_id: The unique report identifier (UUID).

    Returns:
        The cached AnalysisReport.

    Raises:
        HTTPException: If the report is not found in the cache.
    """
    from app.routers.analyze import get_report_cache

    cache = get_report_cache()
    report = cache.get(report_id)

    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report '{report_id}' not found. Reports are cached for a limited time.",
        )

    return report
