"""Pydantic schemas for request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.enums import ScoreCategoryName


class AnalyzeRequest(BaseModel):
    """Request body for the /api/analyze endpoint."""

    repo_url: str = Field(
        ...,
        description="Full GitHub repository URL",
        examples=["https://github.com/fastapi/fastapi"],
    )

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        """Validate that the URL is a valid GitHub repository URL."""
        from app.utils.validators import parse_github_url

        owner, repo = parse_github_url(v)
        # Normalize to canonical form
        return f"https://github.com/{owner}/{repo}"


class RepoInfo(BaseModel):
    """Basic repository information from GitHub API."""

    owner: str = Field(..., description="Repository owner/organization")
    name: str = Field(..., description="Repository name")
    url: str = Field(..., description="Repository URL")
    description: Optional[str] = Field(None, description="Repository description")
    language: Optional[str] = Field(None, description="Primary programming language")
    stars: int = Field(0, description="Star count")
    forks: int = Field(0, description="Fork count")
    open_issues: int = Field(0, description="Open issue count")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    default_branch: str = Field("main", description="Default branch name")
    topics: list[str] = Field(default_factory=list, description="Repository topics")
    has_wiki: bool = Field(False, description="Whether wiki is enabled")
    license_name: Optional[str] = Field(None, description="License SPDX identifier")
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
    breakdown: Dict[ScoreCategoryName, ScoreCategory] = Field(
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
    error_code: Optional[str] = Field(None, description="Machine-readable error code")
