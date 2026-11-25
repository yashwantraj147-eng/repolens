"""Tests for the SQLite persistent report store."""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.models.enums import ScoreCategoryName
from app.models.schemas import AnalysisReport, HealthScore, RepoInfo, ScoreCategory
from app.services.report_store import ReportStore


def create_sample_report(owner: str = "test-owner", name: str = "test-repo", score: int = 85) -> AnalysisReport:
    """Helper to create a valid AnalysisReport instance for testing."""
    repo = RepoInfo(
        owner=owner,
        name=name,
        url=f"https://github.com/{owner}/{name}",
        description="A test repository",
        language="Python",
        stars=120,
        forks=25,
        open_issues=5,
        default_branch="main",
    )
    categories = {
        ScoreCategoryName.README_QUALITY: ScoreCategory(score=90, max_score=100, weight=0.2, details="Good readme"),
        ScoreCategoryName.COMMIT_ACTIVITY: ScoreCategory(score=80, max_score=100, weight=0.15, details="Active"),
        ScoreCategoryName.ISSUE_RESPONSE_TIME: ScoreCategory(score=85, max_score=100, weight=0.15, details="Fast"),
        ScoreCategoryName.TEST_PRESENCE: ScoreCategory(score=90, max_score=100, weight=0.15, details="Tests found"),
        ScoreCategoryName.LICENSE: ScoreCategory(score=100, max_score=100, weight=0.1, details="MIT"),
        ScoreCategoryName.DOCUMENTATION: ScoreCategory(score=80, max_score=100, weight=0.15, details="Docs exist"),
        ScoreCategoryName.CI_SETUP: ScoreCategory(score=85, max_score=100, weight=0.1, details="CI configured"),
    }
    health_score = HealthScore(
        overall=score,
        breakdown=categories,
        grade=HealthScore.compute_grade(score),
    )
    return AnalysisReport(
        report_id=str(uuid.uuid4()),
        repo=repo,
        summary="A test summary",
        architecture_diagram="graph TD; A-->B",
        onboarding_guide="# Onboarding Guide",
        health_score=health_score,
        generated_at=datetime.now(UTC),
    )


class TestReportStore:
    """Test suite for ReportStore persistent SQLite operations."""

    @pytest.fixture
    def store(self) -> ReportStore:
        """Create an in-memory SQLite ReportStore for tests."""
        return ReportStore(db_path=":memory:")

    def test_init_and_empty_count(self, store: ReportStore) -> None:
        """New store should have 0 reports."""
        assert store.count() == 0
        assert store.get_by_id("non-existent") is None
        assert store.get_recent() == []

    def test_save_and_get_by_id(self, store: ReportStore) -> None:
        """Saving a report should allow retrieving it by ID with full fidelity."""
        report = create_sample_report(owner="fastapi", name="fastapi", score=92)
        store.save(report)

        assert store.count() == 1
        fetched = store.get_by_id(report.report_id)
        assert fetched is not None
        assert fetched.report_id == report.report_id
        assert fetched.repo.owner == "fastapi"
        assert fetched.repo.name == "fastapi"
        assert fetched.health_score.overall == 92
        assert fetched.health_score.grade == "A"

    def test_get_latest_for_repo_case_insensitive(self, store: ReportStore) -> None:
        """Lookup by repository should be case-insensitive."""
        report = create_sample_report(owner="Facebook", name="React", score=95)
        store.save(report)

        fetched = store.get_latest_for_repo("facebook", "react")
        assert fetched is not None
        assert fetched.report_id == report.report_id

        fetched_upper = store.get_latest_for_repo("FACEBOOK", "REACT")
        assert fetched_upper is not None
        assert fetched_upper.report_id == report.report_id

    def test_get_latest_for_repo_ttl_fresh(self, store: ReportStore) -> None:
        """Report within TTL should be returned."""
        report = create_sample_report()
        store.save(report)

        # 3600 second TTL should easily encompass fresh report
        fetched = store.get_latest_for_repo(report.repo.owner, report.repo.name, max_age_seconds=3600)
        assert fetched is not None

    def test_get_latest_for_repo_ttl_expired(self, store: ReportStore) -> None:
        """Report older than max_age_seconds should return None."""
        report = create_sample_report()
        # Set timestamp 2 hours in the past
        report.generated_at = datetime.now(UTC) - timedelta(hours=2)
        store.save(report)

        # 1-hour TTL (3600s) should treat 2-hour-old report as expired
        fetched = store.get_latest_for_repo(report.repo.owner, report.repo.name, max_age_seconds=3600)
        assert fetched is None

    def test_get_recent_reports_ordering_and_limit(self, store: ReportStore) -> None:
        """Recent reports should be ordered by created_at descending and respect limit."""
        r1 = create_sample_report(owner="repo", name="one", score=70)
        r1.generated_at = datetime.now(UTC) - timedelta(minutes=10)
        store.save(r1)

        r2 = create_sample_report(owner="repo", name="two", score=80)
        r2.generated_at = datetime.now(UTC) - timedelta(minutes=5)
        store.save(r2)

        r3 = create_sample_report(owner="repo", name="three", score=90)
        r3.generated_at = datetime.now(UTC)
        store.save(r3)

        recent = store.get_recent(limit=2)
        assert len(recent) == 2
        assert recent[0].name == "three"
        assert recent[1].name == "two"

    def test_delete_by_id(self, store: ReportStore) -> None:
        """Deleting an existing report returns True and removes it."""
        report = create_sample_report()
        store.save(report)
        assert store.count() == 1

        deleted = store.delete_by_id(report.report_id)
        assert deleted is True
        assert store.count() == 0
        assert store.get_by_id(report.report_id) is None

        # Deleting non-existent returns False
        assert store.delete_by_id("fake-id") is False
