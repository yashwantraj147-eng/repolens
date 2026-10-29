"""Comprehensive tests for the repository health scoring engine.

Targeting >= 80% test coverage across all scoring functions and edge cases.
"""

from datetime import datetime, timezone, timedelta
import pytest

from app.models.enums import ScoreCategoryName
from app.models.schemas import RepoInfo
from app.services.scoring_engine import ScoringEngine, CATEGORY_WEIGHTS


@pytest.fixture
def base_repo_info() -> RepoInfo:
    """Create a minimal RepoInfo instance for testing."""
    return RepoInfo(
        owner="test-owner",
        name="test-repo",
        url="https://github.com/test-owner/test-repo",
        description="A test repository for unit tests",
        language="Python",
        stars=100,
        forks=20,
        open_issues=5,
        created_at=datetime.now(timezone.utc) - timedelta(days=365),
        updated_at=datetime.now(timezone.utc),
        default_branch="main",
        topics=["testing", "python"],
        has_wiki=True,
        license_name="MIT",
        size=1024,
    )


class TestScoringEngineCalculation:
    """Tests for the overall scoring calculation and grading."""

    def test_default_weights_sum_to_one(self) -> None:
        """Verify standard category weights sum up to 1.0."""
        total_weight = sum(CATEGORY_WEIGHTS.values())
        assert pytest.approx(total_weight, 0.001) == 1.0

    def test_calculate_score_perfect_repo(self, base_repo_info: RepoInfo) -> None:
        """A well-equipped repository should score high (A grade)."""
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)

        readme = """# Test Project
[![CI](https://img.shields.io/badge/ci-pass-green)]()
[![Codecov](https://img.shields.io/badge/coverage-100-green)]()

This is a comprehensive description of the test project that exceeds five hundred characters easily
to ensure full scoring points for length and depth. We include extensive explanations of what this
project does and why it is beneficial for the developer ecosystem. It is robust, resilient, and well-tested.

## Installation
```bash
pip install test-repo
```

## Quick Start
```python
import test_repo
test_repo.run()
```

## Documentation
Refer to official docs.
![Screenshot](https://example.com/logo.png)
"""
        file_tree = [
            {"path": "README.md", "type": "blob"},
            {"path": "LICENSE", "type": "blob"},
            {"path": "CONTRIBUTING.md", "type": "blob"},
            {"path": "CODE_OF_CONDUCT.md", "type": "blob"},
            {"path": "CHANGELOG.md", "type": "blob"},
            {"path": "pytest.ini", "type": "blob"},
            {"path": ".coveragerc", "type": "blob"},
            {"path": "docs/index.md", "type": "blob"},
            {"path": "tests/test_main.py", "type": "blob"},
            {"path": "tests/test_util.py", "type": "blob"},
            {"path": "tests/test_service.py", "type": "blob"},
            {"path": "tests/test_api.py", "type": "blob"},
            {"path": "tests/test_extra.py", "type": "blob"},
            {"path": ".github/workflows/ci.yml", "type": "blob"},
        ]

        recent_commits = [
            {
                "commit": {
                    "committer": {
                        "date": (now - timedelta(days=i)).isoformat()
                    }
                }
            }
            for i in range(55)
        ]

        closed_issues = [
            {
                "created_at": (now - timedelta(hours=10)).isoformat(),
                "closed_at": (now - timedelta(hours=2)).isoformat(),
            },
            {
                "created_at": (now - timedelta(hours=20)).isoformat(),
                "closed_at": (now - timedelta(hours=8)).isoformat(),
            },
        ]

        score = engine.calculate_score(
            repo_info=base_repo_info,
            readme_content=readme,
            file_tree=file_tree,
            recent_commits=recent_commits,
            closed_issues=closed_issues,
        )

        assert score.overall >= 90
        assert score.grade in ("A", "A+")
        assert len(score.breakdown) == 7

    def test_calculate_score_empty_repo(self, base_repo_info: RepoInfo) -> None:
        """An empty repository with no docs/tests/license should receive an F."""
        engine = ScoringEngine()
        base_repo_info.license_name = None
        base_repo_info.has_wiki = False

        score = engine.calculate_score(
            repo_info=base_repo_info,
            readme_content=None,
            file_tree=[],
            recent_commits=[],
            closed_issues=[],
        )

        assert score.overall < 50
        assert score.grade == "F"

    def test_grade_boundaries(self) -> None:
        """Verify all letter grade thresholds."""
        from app.models.schemas import HealthScore

        assert HealthScore.compute_grade(96) == "A+"
        assert HealthScore.compute_grade(92) == "A"
        assert HealthScore.compute_grade(87) == "A-"
        assert HealthScore.compute_grade(82) == "B+"
        assert HealthScore.compute_grade(76) == "B"
        assert HealthScore.compute_grade(71) == "B-"
        assert HealthScore.compute_grade(67) == "C+"
        assert HealthScore.compute_grade(62) == "C"
        assert HealthScore.compute_grade(57) == "C-"
        assert HealthScore.compute_grade(52) == "D"
        assert HealthScore.compute_grade(45) == "F"


class TestReadmeScoring:
    """Tests for README evaluation."""

    def test_missing_readme(self) -> None:
        engine = ScoringEngine()
        result = engine.score_readme_quality(None)
        assert result.score == 0
        assert "No README found" in result.details

    def test_short_readme_without_formatting(self) -> None:
        engine = ScoringEngine()
        result = engine.score_readme_quality("Just a short sentence.")
        assert result.score == 0
        assert "under 200 characters" in result.details

    def test_moderate_readme_with_one_heading(self) -> None:
        engine = ScoringEngine()
        content = "# Title\n" + ("a" * 250)
        result = engine.score_readme_quality(content)
        assert result.score == 20  # 10 (len) + 10 (1 heading)
        assert "Moderate length" in result.details

    def test_comprehensive_readme_components(self) -> None:
        engine = ScoringEngine()
        content = (
            "# Main Heading\n"
            "## Section 1\n"
            "### Section 2\n"
            "Here is shields.io badge: https://img.shields.io/badge/status-active\n"
            "To install run: pip install package\n"
            "```python\nprint('code example')\n```\n"
            "<img src='demo.gif' alt='demo' />\n"
            + ("Some long description text filling up characters. " * 15)
        )
        result = engine.score_readme_quality(content)
        assert result.score == 100


class TestCommitActivityScoring:
    """Tests for commit activity and recency calculation."""

    def test_no_commits(self) -> None:
        engine = ScoringEngine()
        result = engine.score_commit_activity([])
        assert result.score == 0
        assert "No commits" in result.details

    def test_low_commit_count(self) -> None:
        engine = ScoringEngine()
        commits = [{"commit": {"committer": {"date": "2020-01-01T00:00:00Z"}}}] * 3
        result = engine.score_commit_activity(commits)
        assert result.score == 25

    def test_medium_commit_count(self) -> None:
        engine = ScoringEngine()
        commits = [{"commit": {"committer": {"date": "2020-01-01T00:00:00Z"}}}] * 8
        result = engine.score_commit_activity(commits)
        assert result.score == 40

    def test_active_commit_count(self) -> None:
        engine = ScoringEngine()
        commits = [{"commit": {"committer": {"date": "2020-01-01T00:00:00Z"}}}] * 30
        result = engine.score_commit_activity(commits)
        assert result.score == 70

    def test_very_active_with_recency_bonus(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        recent_date = (now - timedelta(days=2)).isoformat()
        commits = [{"commit": {"committer": {"date": recent_date}}}] + [
            {"commit": {"committer": {"date": "2020-01-01T00:00:00Z"}}}
        ] * 60
        result = engine.score_commit_activity(commits)
        assert result.score == 100  # 90 + 10 bonus capped at 100
        assert "bonus" in result.details

    def test_unparseable_commit_date(self) -> None:
        engine = ScoringEngine()
        commits = [{"commit": {"committer": {"date": "invalid-date"}}}]
        result = engine.score_commit_activity(commits)
        assert result.score == 25
        assert "Could not determine last commit date" in result.details


class TestIssueResponseTimeScoring:
    """Tests for issue response time calculation."""

    def test_empty_issues(self) -> None:
        engine = ScoringEngine()
        result = engine.score_issue_response_time([])
        assert result.score == 50
        assert "No closed issues" in result.details

    def test_invalid_issue_timestamps(self) -> None:
        engine = ScoringEngine()
        issues = [{"created_at": "not-a-date", "closed_at": "bad-date"}]
        result = engine.score_issue_response_time(issues)
        assert result.score == 50

    def test_fast_response_less_than_one_day(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(hours=12)).isoformat(),
                "closed_at": now.isoformat(),
            }
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 100
        assert "excellent" in result.details

    def test_medium_response_under_three_days(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(days=2)).isoformat(),
                "closed_at": now.isoformat(),
            }
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 80

    def test_acceptable_response_under_seven_days(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(days=5)).isoformat(),
                "closed_at": now.isoformat(),
            }
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 60

    def test_slow_response_under_thirty_days(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(days=20)).isoformat(),
                "closed_at": now.isoformat(),
            }
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 30

    def test_very_slow_response_over_thirty_days(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(days=45)).isoformat(),
                "closed_at": now.isoformat(),
            }
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 10

    def test_even_count_median(self) -> None:
        engine = ScoringEngine()
        now = datetime.now(timezone.utc)
        issues = [
            {
                "created_at": (now - timedelta(hours=2)).isoformat(),
                "closed_at": now.isoformat(),
            },
            {
                "created_at": (now - timedelta(hours=6)).isoformat(),
                "closed_at": now.isoformat(),
            },
        ]
        result = engine.score_issue_response_time(issues)
        assert result.score == 100


class TestTestPresenceScoring:
    """Tests for test presence detection."""

    def test_no_tests(self) -> None:
        engine = ScoringEngine()
        result = engine.score_test_presence(["src/main.py", "README.md"])
        assert result.score == 0
        assert "No test infrastructure" in result.details

    def test_partial_tests_single_file(self) -> None:
        engine = ScoringEngine()
        result = engine.score_test_presence(["test_app.py"])
        assert result.score == 20  # single test file

    def test_full_test_infrastructure(self) -> None:
        engine = ScoringEngine()
        files = [
            "tests/test_a.py",
            "tests/test_b.py",
            "tests/test_c.py",
            "tests/test_d.py",
            "tests/test_e.py",
            "pytest.ini",
            ".coveragerc",
        ]
        result = engine.score_test_presence(files)
        # 30 (test dir) + 35 (>=5 test files) + 20 (pytest.ini) + 15 (coverage) = 100
        assert result.score == 100


class TestLicenseScoring:
    """Tests for license scoring."""

    def test_valid_spdx_license(self, base_repo_info: RepoInfo) -> None:
        engine = ScoringEngine()
        base_repo_info.license_name = "Apache-2.0"
        result = engine.score_license(base_repo_info, ["LICENSE"])
        assert result.score == 100
        assert "Apache-2.0" in result.details

    def test_unrecognized_license_file(self, base_repo_info: RepoInfo) -> None:
        engine = ScoringEngine()
        base_repo_info.license_name = None
        result = engine.score_license(base_repo_info, ["license.txt"])
        assert result.score == 80
        assert "License file found" in result.details

    def test_no_license(self, base_repo_info: RepoInfo) -> None:
        engine = ScoringEngine()
        base_repo_info.license_name = None
        result = engine.score_license(base_repo_info, ["src/index.js"])
        assert result.score == 0
        assert "No license detected" in result.details


class TestDocumentationScoring:
    """Tests for repository documentation."""

    def test_all_documentation_elements(self, base_repo_info: RepoInfo) -> None:
        engine = ScoringEngine()
        base_repo_info.has_wiki = True
        files = [
            "docs/guide.md",
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md",
            "CHANGELOG.md",
        ]
        result = engine.score_documentation(base_repo_info, files)
        # 30 + 25 + 15 + 15 + 15 = 100
        assert result.score == 100

    def test_missing_all_documentation(self, base_repo_info: RepoInfo) -> None:
        engine = ScoringEngine()
        base_repo_info.has_wiki = False
        result = engine.score_documentation(base_repo_info, ["src/main.py"])
        assert result.score == 0


class TestCiSetupScoring:
    """Tests for CI/CD setup."""

    def test_no_ci(self) -> None:
        engine = ScoringEngine()
        result = engine.score_ci_setup(["src/main.py"])
        assert result.score == 0

    def test_single_ci_github_actions(self) -> None:
        engine = ScoringEngine()
        result = engine.score_ci_setup([".github/workflows/main.yml"])
        assert result.score == 50
        assert "GitHub Actions" in result.details

    def test_multiple_ci_systems(self) -> None:
        engine = ScoringEngine()
        result = engine.score_ci_setup([
            ".github/workflows/main.yml",
            ".travis.yml",
            "Jenkinsfile",
        ])
        # 50 + 25 + 25 = 100
        assert result.score == 100

