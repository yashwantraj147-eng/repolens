"""Unit tests for RepoLens head-to-head repository comparison."""

from datetime import datetime, timezone
import pytest
from unittest.mock import AsyncMock, patch

from app.models.enums import ScoreCategoryName
from app.models.schemas import (
    AnalysisReport,
    HealthScore,
    RepoInfo,
    ScoreCategory,
    CompareRequest,
)
from app.services.comparison_engine import ComparisonEngine


def create_mock_report(
    owner: str,
    name: str,
    score: int,
    stars: int,
    forks: int,
    issues: int,
    security_score: int = 80,
) -> AnalysisReport:
    """Helper to create a realistic AnalysisReport."""
    breakdown = {
        ScoreCategoryName.README_QUALITY: ScoreCategory(score=90, max_score=100, weight=0.15, details="Rich"),
        ScoreCategoryName.TEST_PRESENCE: ScoreCategory(score=85, max_score=100, weight=0.15, details="Unit tests"),
        ScoreCategoryName.SECURITY_POSTURE: ScoreCategory(score=security_score, max_score=100, weight=0.15, details="Security config"),
        ScoreCategoryName.COMMIT_ACTIVITY: ScoreCategory(score=75, max_score=100, weight=0.15, details="Recent"),
        ScoreCategoryName.DOCUMENTATION: ScoreCategory(score=80, max_score=100, weight=0.15, details="Docs"),
        ScoreCategoryName.CI_SETUP: ScoreCategory(score=100, max_score=100, weight=0.10, details="Actions"),
        ScoreCategoryName.ISSUE_RESPONSE_TIME: ScoreCategory(score=70, max_score=100, weight=0.10, details="Issues"),
        ScoreCategoryName.LICENSE: ScoreCategory(score=100, max_score=100, weight=0.05, details="MIT"),
    }
    return AnalysisReport(
        report_id=f"rep_{name}",
        repo=RepoInfo(
            owner=owner,
            name=name,
            url=f"https://github.com/{owner}/{name}",
            stars=stars,
            forks=forks,
            open_issues=issues,
        ),
        summary="A test repository",
        architecture_diagram="graph TD\n  ROOT --> SRC",
        onboarding_guide="Setup guide",
        health_score=HealthScore(
            overall=score,
            grade=HealthScore.compute_grade(score),
            breakdown=breakdown,
        ),
        generated_at=datetime.now(timezone.utc),
    )


class TestComparisonEngine:
    """Tests for ComparisonEngine metric and verdict calculation."""

    def test_repo_a_wins(self) -> None:
        rep_a = create_mock_report("fastapi", "fastapi", score=90, stars=70000, forks=6000, issues=500, security_score=95)
        rep_b = create_mock_report("pallets", "flask", score=78, stars=65000, forks=16000, issues=10, security_score=50)

        engine = ComparisonEngine()
        result = engine.compare(rep_a, rep_b)

        assert result.overall_winner == "repo_a"
        assert result.score_diff == 12
        assert "fastapi/fastapi takes the lead" in result.verdict_summary
        assert len(result.categories) == 8

        # Security category delta check
        sec_cat = next(c for c in result.categories if c.category == ScoreCategoryName.SECURITY_POSTURE)
        assert sec_cat.score_a == 95
        assert sec_cat.score_b == 50
        assert sec_cat.diff == 45
        assert sec_cat.winner == "repo_a"

        # Stars check
        assert result.metrics.stars_diff == 5000
        assert result.metrics.stars_winner == "repo_a"
        assert result.metrics.forks_winner == "repo_b"

    def test_repo_b_wins(self) -> None:
        rep_a = create_mock_report("repo1", "alpha", score=65, stars=100, forks=10, issues=5)
        rep_b = create_mock_report("repo2", "beta", score=85, stars=500, forks=50, issues=2)

        engine = ComparisonEngine()
        result = engine.compare(rep_a, rep_b)

        assert result.overall_winner == "repo_b"
        assert result.score_diff == -20
        assert "repo2/beta takes the lead" in result.verdict_summary

    def test_tie_comparison(self) -> None:
        rep_a = create_mock_report("repo1", "alpha", score=80, stars=100, forks=10, issues=5)
        rep_b = create_mock_report("repo2", "beta", score=80, stars=100, forks=10, issues=5)

        engine = ComparisonEngine()
        result = engine.compare(rep_a, rep_b)

        assert result.overall_winner == "tie"
        assert result.score_diff == 0
        assert "evenly matched" in result.verdict_summary


class TestCompareRouter:
    """Tests for POST /api/compare router."""

    @pytest.mark.asyncio
    async def test_compare_endpoint_success(self) -> None:
        from app.routers.compare import compare_repositories

        rep_a = create_mock_report("fastapi", "fastapi", score=88, stars=70000, forks=6000, issues=500)
        rep_b = create_mock_report("pallets", "flask", score=80, stars=65000, forks=16000, issues=10)

        with patch("app.routers.compare.analyze_repo", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.side_effect = [rep_a, rep_b]

            req = CompareRequest(
                repo_a="fastapi/fastapi",
                repo_b="pallets/flask",
            )
            response = await compare_repositories(req)

            assert response.repo_a.repo.name == "fastapi"
            assert response.repo_b.repo.name == "flask"
            assert response.comparison.overall_winner == "repo_a"
            assert response.comparison.score_diff == 8

    def test_invalid_repo_url_rejected(self) -> None:
        with pytest.raises(ValueError):
            CompareRequest(
                repo_a="not-a-valid-github-url",
                repo_b="fastapi/fastapi",
            )
