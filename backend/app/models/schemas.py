"""Pydantic schemas for request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ScoreCategoryName


class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""

    repo_url: str = Field(
        ...,
        description="Full GitHub repository URL",
        examples=["https://github.com/fastapi/fastapi"],
    )
    force_refresh: bool = Field(
        default=False,
        description="Bypass cache and force a fresh analysis from GitHub API",
    )

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that the URL is a valid GitHub repository URL."""
        from app.utils.validators import parse_github_url

        v = v.strip()
        if not v.startswith(("http://", "https://", "github.com/")) and "/" in v and len(v.split("/")) == 2:
            v = f"https://github.com/{v}"

        owner, repo = parse_github_url(v)
        # Normalize to canonical form
        return f"https://github.com/{owner}/{repo}"


class RepoInfo(BaseModel):
    """Basic repository information from GitHub API."""

    owner: str = Field(..., description="Repository owner/organization")
    name: str = Field(..., description="Repository name")
    url: str = Field(..., description="Repository URL")
    description: str | None = Field(None, description="Repository description")
    language: str | None = Field(None, description="Primary programming language")
    stars: int = Field(0, description="Star count")
    forks: int = Field(0, description="Fork count")
    open_issues: int = Field(0, description="Open issue count")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")
    default_branch: str = Field("main", description="Default branch name")
    topics: list[str] = Field(default_factory=list, description="Repository topics")
    has_wiki: bool = Field(False, description="Whether wiki is enabled")
    license_name: str | None = Field(None, description="License SPDX identifier")
    size: int = Field(0, description="Repository size in KB")


class ScoreCategory(BaseModel):
    """Individual score category result."""

    score: int = Field(..., ge=0, le=100, description="Score for this category")
    max_score: int = Field(default=100, description="Maximum possible score")
    weight: float = Field(..., ge=0, le=1, description="Weight in overall score")
    details: str = Field(..., description="Human-readable explanation")


class HealthScore(BaseModel):
    """Overall repository health score with breakdown."""

    overall: int = Field(..., ge=0, le=100, description="Weighted overall score")
    breakdown: dict[ScoreCategoryName, ScoreCategory] = Field(
        ..., description="Per-category score breakdown"
    )
    grade: str = Field(..., description="Letter grade (A+ to F)")

    @staticmethod
    def compute_grade(score: int) -> str:
        """Convert a numeric score to a letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"


class AnalysisReport(BaseModel):
    """Complete analysis report for a repository."""

    report_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique report identifier",
    )
    repo: RepoInfo = Field(..., description="Repository information")
    summary: str = Field(..., description="Plain-English summary of the repo")
    architecture_diagram: str = Field(
        ..., description="Mermaid diagram markup"
    )
    onboarding_guide: str = Field(
        ..., description="Getting Started guide in Markdown"
    )
    health_score: HealthScore = Field(..., description="Health score with breakdown")
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Report generation timestamp",
    )


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    error_code: str | None = Field(None, description="Machine-readable error code")


class RecentReportItem(BaseModel):
    """Summary item for recently analyzed repository listing."""

    report_id: str = Field(..., description="Unique report identifier")
    owner: str = Field(..., description="Repository owner")
    name: str = Field(..., description="Repository name")
    url: str = Field(..., description="Repository URL")
    stars: int = Field(0, description="Star count")
    language: str | None = Field(None, description="Primary programming language")
    overall_score: int = Field(..., ge=0, le=100, description="Overall health score")
    grade: str = Field(..., description="Letter grade")
    generated_at: datetime = Field(..., description="When the report was generated")


class CompareRequest(BaseModel):
    """Request body for head-to-head repository comparison."""

    repo_a: str = Field(..., description="First GitHub repository URL or owner/repo")
    repo_b: str = Field(..., description="Second GitHub repository URL or owner/repo")
    force_refresh: bool = Field(
        default=False,
        description="Bypass cache and force fresh analysis for both repositories",
    )

    @field_validator("repo_a", "repo_b")
    @classmethod
    def validate_repo_urls(cls, v: str) -> str:
        """Validate and normalize repository URL."""
        from app.utils.validators import parse_github_url

        v = v.strip()
        if not v.startswith(("http://", "https://", "github.com/")) and "/" in v and len(v.split("/")) == 2:
            v = f"https://github.com/{v}"

        owner, repo = parse_github_url(v)
        return f"https://github.com/{owner}/{repo}"


class CategoryComparison(BaseModel):
    """Comparison metric for a specific score category."""

    category: ScoreCategoryName = Field(..., description="Category identifier")
    name: str = Field(..., description="Category display name")
    score_a: int = Field(..., description="Score for repo A")
    score_b: int = Field(..., description="Score for repo B")
    winner: str = Field(..., description="'repo_a', 'repo_b', or 'tie'")
    diff: int = Field(..., description="Score difference (repo_a - repo_b)")
    details_a: str = Field(..., description="Finding details for repo A")
    details_b: str = Field(..., description="Finding details for repo B")


class MetricComparison(BaseModel):
    """Comparison of community and activity metrics."""

    stars_diff: int = Field(..., description="Difference in stars (A - B)")
    forks_diff: int = Field(..., description="Difference in forks (A - B)")
    open_issues_diff: int = Field(..., description="Difference in open issues (A - B)")
    stars_winner: str = Field(..., description="'repo_a', 'repo_b', or 'tie'")
    forks_winner: str = Field(..., description="'repo_a', 'repo_b', or 'tie'")


class ComparisonMetrics(BaseModel):
    """Full comparison analysis between two repositories."""

    overall_winner: str = Field(..., description="'repo_a', 'repo_b', or 'tie'")
    score_diff: int = Field(..., description="Overall health score diff (A - B)")
    categories: list[CategoryComparison] = Field(..., description="Per-category comparisons")
    metrics: MetricComparison = Field(..., description="Community metrics comparison")
    verdict_summary: str = Field(..., description="Plain-English comparison conclusion")


class CompareResponse(BaseModel):
    """Response returned by /api/compare."""

    repo_a: AnalysisReport = Field(..., description="Full analysis for repo A")
    repo_b: AnalysisReport = Field(..., description="Full analysis for repo B")
    comparison: ComparisonMetrics = Field(..., description="Comparative metrics and verdict")


