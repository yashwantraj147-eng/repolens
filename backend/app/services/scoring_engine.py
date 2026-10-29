"""Repository health scoring engine.

Evaluates repositories across 7 categories and produces a weighted
overall health score from 0 to 100.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.models.enums import ScoreCategoryName
from app.models.schemas import HealthScore, RepoInfo, ScoreCategory


# Category weights (must sum to 1.0)
CATEGORY_WEIGHTS: Dict[ScoreCategoryName, float] = {
    ScoreCategoryName.README_QUALITY: 0.20,
    ScoreCategoryName.COMMIT_ACTIVITY: 0.15,
    ScoreCategoryName.ISSUE_RESPONSE_TIME: 0.10,
    ScoreCategoryName.TEST_PRESENCE: 0.20,
    ScoreCategoryName.LICENSE: 0.10,
    ScoreCategoryName.DOCUMENTATION: 0.15,
    ScoreCategoryName.CI_SETUP: 0.10,
}


class ScoringEngine:
    """Calculates repository health scores across multiple categories.

    Each category is scored independently on a 0-100 scale, then
    combined using configurable weights to produce an overall score.
    """

    def __init__(
        self,
        weights: Optional[Dict[ScoreCategoryName, float]] = None,
    ) -> None:
        """Initialize the scoring engine.

        Args:
            weights: Optional custom weights for scoring categories.
                     Must sum to 1.0. Defaults to CATEGORY_WEIGHTS.
        """
        self.weights = weights or CATEGORY_WEIGHTS

    def calculate_score(
        self,
        repo_info: RepoInfo,
        readme_content: Optional[str] = None,
        file_tree: Optional[List[Dict[str, Any]]] = None,
        recent_commits: Optional[List[Dict[str, Any]]] = None,
        closed_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> HealthScore:
        """Calculate the overall health score for a repository.

        Args:
            repo_info: Basic repository metadata.
            readme_content: Raw README text content.
            file_tree: List of file tree entries.
            recent_commits: List of recent commit data.
            closed_issues: List of recently closed issues.

        Returns:
            HealthScore with overall score, grade, and per-category breakdown.
        """
        file_tree = file_tree or []
        recent_commits = recent_commits or []
        closed_issues = closed_issues or []

        # Get all file paths for convenience
        file_paths = [entry["path"] for entry in file_tree]

        # Calculate each category
        breakdown: Dict[ScoreCategoryName, ScoreCategory] = {
            ScoreCategoryName.README_QUALITY: self.score_readme_quality(
                readme_content
            ),
            ScoreCategoryName.COMMIT_ACTIVITY: self.score_commit_activity(
                recent_commits
            ),
            ScoreCategoryName.ISSUE_RESPONSE_TIME: self.score_issue_response_time(
                closed_issues
            ),
            ScoreCategoryName.TEST_PRESENCE: self.score_test_presence(
                file_paths
            ),
            ScoreCategoryName.LICENSE: self.score_license(
                repo_info, file_paths
            ),
            ScoreCategoryName.DOCUMENTATION: self.score_documentation(
                repo_info, file_paths
            ),
            ScoreCategoryName.CI_SETUP: self.score_ci_setup(file_paths),
        }

        # Calculate weighted overall score
        overall = round(
            sum(
                breakdown[cat].score * breakdown[cat].weight
                for cat in breakdown
            )
        )
        overall = max(0, min(100, overall))

        grade = HealthScore.compute_grade(overall)

        return HealthScore(
            overall=overall,
            breakdown=breakdown,
            grade=grade,
        )

    def score_readme_quality(
        self, readme_content: Optional[str]
    ) -> ScoreCategory:
        """Score the quality of the repository README.

        Criteria:
        - Length >= 500 chars (+20)
        - Has headings/sections (+20)
        - Has code blocks (+20)
        - Has badges (+15)
        - Has install/setup instructions (+15)
        - Has images or GIFs (+10)

        Args:
            readme_content: Raw README text, or None if missing.

        Returns:
            ScoreCategory with score and details.
        """
        if not readme_content:
            return ScoreCategory(
                score=0,
                weight=self.weights[ScoreCategoryName.README_QUALITY],
                details="No README found.",
            )

        score = 0
        findings: list[str] = []

        # Length check
        if len(readme_content) >= 500:
            score += 20
            findings.append("Good length (500+ characters)")
        elif len(readme_content) >= 200:
            score += 10
            findings.append("Moderate length (200+ characters)")
        else:
            findings.append("README is short (under 200 characters)")

        # Headings
        heading_pattern = re.compile(r"^#{1,6}\s+.+", re.MULTILINE)
        headings = heading_pattern.findall(readme_content)
        if len(headings) >= 3:
            score += 20
            findings.append(f"Well-structured with {len(headings)} sections")
        elif len(headings) >= 1:
            score += 10
            findings.append(f"Has {len(headings)} heading(s)")
        else:
            findings.append("No section headings found")

        # Code blocks
        code_block_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
        code_blocks = code_block_pattern.findall(readme_content)
        if code_blocks:
            score += 20
            findings.append(f"Includes {len(code_blocks)} code example(s)")
        else:
            findings.append("No code examples found")

        # Badges
        badge_patterns = [
            r"\[!\[.*?\]\(.*?\)\]\(.*?\)",  # [![alt](img)](link)
            r"!\[.*?badge.*?\]",              # ![...badge...]
            r"img\.shields\.io",              # shields.io URLs
            r"badge",                         # generic badge references
        ]
        has_badges = any(
            re.search(p, readme_content, re.IGNORECASE) for p in badge_patterns
        )
        if has_badges:
            score += 15
            findings.append("Has badges/status indicators")
        else:
            findings.append("No badges found")

        # Install/setup instructions
        install_patterns = [
            r"(?i)install",
            r"(?i)getting\s+started",
            r"(?i)quick\s*start",
            r"(?i)setup",
            r"(?i)pip\s+install",
            r"(?i)npm\s+install",
            r"(?i)yarn\s+add",
            r"(?i)brew\s+install",
            r"(?i)docker",
        ]
        has_install = any(
            re.search(p, readme_content) for p in install_patterns
        )
        if has_install:
            score += 15
            findings.append("Contains installation/setup instructions")
        else:
            findings.append("No installation instructions found")

        # Images or GIFs
        image_patterns = [
            r"!\[.*?\]\(.*?\.(png|jpg|jpeg|gif|svg|webp)",
            r"<img\s+",
            r"\.gif\b",
        ]
        has_images = any(
            re.search(p, readme_content, re.IGNORECASE) for p in image_patterns
        )
        if has_images:
            score += 10
            findings.append("Includes visual content (images/GIFs)")
        else:
            findings.append("No images or visual content")

        return ScoreCategory(
            score=min(score, 100),
            weight=self.weights[ScoreCategoryName.README_QUALITY],
            details="; ".join(findings),
        )

    def score_commit_activity(
        self, recent_commits: List[Dict[str, Any]]
    ) -> ScoreCategory:
        """Score recent commit activity.

        Based on number of commits in the last 90 days, with a
        recency bonus if the last commit was within the last 7 days.

        Args:
            recent_commits: List of commit data from the last 90 days.

        Returns:
            ScoreCategory with score and details.
        """
        count = len(recent_commits)
        findings: list[str] = []

        if count == 0:
            score = 0
            findings.append("No commits in the last 90 days")
        elif count <= 5:
            score = 25
            findings.append(f"{count} commit(s) in the last 90 days — low activity")
        elif count <= 10:
            score = 40
            findings.append(f"{count} commits in the last 90 days — some activity")
        elif count <= 50:
            score = 70
            findings.append(f"{count} commits in the last 90 days — active")
        else:
            score = 90
            findings.append(f"{count} commits in the last 90 days — very active")

        # Recency bonus: check if the most recent commit is within 7 days
        if recent_commits:
            try:
                latest = recent_commits[0]
                commit_date_str = latest.get("commit", {}).get("committer", {}).get("date", "")
                if commit_date_str:
                    commit_date = datetime.fromisoformat(
                        commit_date_str.replace("Z", "+00:00")
                    )
                    days_since = (datetime.now(timezone.utc) - commit_date).days
                    if days_since <= 7:
                        score = min(score + 10, 100)
                        findings.append(f"Last commit {days_since} day(s) ago — recent activity bonus")
                    else:
                        findings.append(f"Last commit {days_since} days ago")
            except (ValueError, KeyError, TypeError):
                findings.append("Could not determine last commit date")

        return ScoreCategory(
            score=score,
            weight=self.weights[ScoreCategoryName.COMMIT_ACTIVITY],
            details="; ".join(findings),
        )

    def score_issue_response_time(
        self, closed_issues: List[Dict[str, Any]]
    ) -> ScoreCategory:
        """Score issue response time based on closed issues.

        Measures median time from issue creation to first response
        (approximated by close time for simplicity).

        Args:
            closed_issues: List of recently closed issue data.

        Returns:
            ScoreCategory with score and details.
        """
        if not closed_issues:
            return ScoreCategory(
                score=50,
                weight=self.weights[ScoreCategoryName.ISSUE_RESPONSE_TIME],
                details="No closed issues found to analyze — neutral score assigned.",
            )

        response_times_hours: list[float] = []
        for issue in closed_issues:
            try:
                created = datetime.fromisoformat(
                    issue["created_at"].replace("Z", "+00:00")
                )
                closed = datetime.fromisoformat(
                    issue["closed_at"].replace("Z", "+00:00")
                )
                delta = (closed - created).total_seconds() / 3600  # hours
                response_times_hours.append(delta)
            except (ValueError, KeyError, TypeError):
                continue

        if not response_times_hours:
            return ScoreCategory(
                score=50,
                weight=self.weights[ScoreCategoryName.ISSUE_RESPONSE_TIME],
                details="Could not parse issue timestamps — neutral score assigned.",
            )

        # Calculate median
        sorted_times = sorted(response_times_hours)
        n = len(sorted_times)
        if n % 2 == 0:
            median_hours = (sorted_times[n // 2 - 1] + sorted_times[n // 2]) / 2
        else:
            median_hours = sorted_times[n // 2]

        median_days = median_hours / 24

        if median_days < 1:
            score = 100
            detail = f"Median response time: {median_hours:.0f} hours — excellent"
        elif median_days < 3:
            score = 80
            detail = f"Median response time: {median_days:.1f} days — good"
        elif median_days < 7:
            score = 60
            detail = f"Median response time: {median_days:.1f} days — acceptable"
        elif median_days < 30:
            score = 30
            detail = f"Median response time: {median_days:.0f} days — slow"
        else:
            score = 10
            detail = f"Median response time: {median_days:.0f} days — very slow"

        return ScoreCategory(
            score=score,
            weight=self.weights[ScoreCategoryName.ISSUE_RESPONSE_TIME],
            details=f"{detail} (based on {len(response_times_hours)} issues)",
        )

    def score_test_presence(
        self, file_paths: List[str]
    ) -> ScoreCategory:
        """Score the presence and coverage of tests.

        Checks for:
        - Test directories (tests/, test/, __tests__/, spec/)
        - Test files (test_*.py, *.test.js, *_test.go, etc.)
        - Test configuration files (pytest.ini, jest.config.*, etc.)
        - Test scripts in package.json

        Args:
            file_paths: List of all file paths in the repository.

        Returns:
            ScoreCategory with score and details.
        """
        score = 0
        findings: list[str] = []

        # Normalize paths to lowercase for matching
        lower_paths = [p.lower() for p in file_paths]

        # Test directories
        test_dirs = {"tests", "test", "__tests__", "spec", "specs"}
        found_dirs = [
            d for d in test_dirs
            if any(p.startswith(d + "/") or p == d for p in lower_paths)
        ]
        if found_dirs:
            score += 30
            findings.append(f"Test directory found: {', '.join(found_dirs)}")

        # Test files
        test_file_patterns = [
            r"test_.*\.py$",
            r".*_test\.py$",
            r".*\.test\.(js|jsx|ts|tsx)$",
            r".*\.spec\.(js|jsx|ts|tsx)$",
            r".*_test\.go$",
            r".*Test\.java$",
            r".*_spec\.rb$",
        ]
        test_files = [
            p for p in file_paths
            if any(re.search(pattern, p) for pattern in test_file_patterns)
        ]
        if len(test_files) >= 5:
            score += 35
            findings.append(f"{len(test_files)} test files found — comprehensive")
        elif len(test_files) >= 1:
            score += 20
            findings.append(f"{len(test_files)} test file(s) found")
        else:
            findings.append("No test files detected")

        # Test configuration files
        test_configs = [
            "pytest.ini",
            "setup.cfg",
            "pyproject.toml",
            "jest.config.js",
            "jest.config.ts",
            "jest.config.mjs",
            "vitest.config.js",
            "vitest.config.ts",
            ".mocharc.yml",
            "karma.conf.js",
            "phpunit.xml",
            "phpunit.xml.dist",
        ]
        found_configs = [
            c for c in test_configs
            if c.lower() in lower_paths
        ]
        if found_configs:
            score += 20
            findings.append(f"Test config found: {', '.join(found_configs)}")

        # Coverage configuration
        coverage_indicators = [
            ".coveragerc",
            "coverage",
            "codecov",
            "coveralls",
        ]
        has_coverage = any(
            any(ind in p.lower() for ind in coverage_indicators)
            for p in file_paths
        )
        if has_coverage:
            score += 15
            findings.append("Coverage tracking configured")

        if score == 0:
            findings = ["No test infrastructure detected"]

        return ScoreCategory(
            score=min(score, 100),
            weight=self.weights[ScoreCategoryName.TEST_PRESENCE],
            details="; ".join(findings),
        )

    def score_license(
        self, repo_info: RepoInfo, file_paths: List[str]
    ) -> ScoreCategory:
        """Score license presence and type.

        Args:
            repo_info: Repository metadata (includes license info from API).
            file_paths: List of file paths in the repository.

        Returns:
            ScoreCategory with score and details.
        """
        lower_paths = [p.lower() for p in file_paths]

        has_license_file = any(
            p in ("license", "license.md", "license.txt", "licence", "licence.md", "copying")
            for p in lower_paths
        )

        if repo_info.license_name and repo_info.license_name != "NOASSERTION":
            return ScoreCategory(
                score=100,
                weight=self.weights[ScoreCategoryName.LICENSE],
                details=f"Licensed under {repo_info.license_name}.",
            )
        elif has_license_file:
            return ScoreCategory(
                score=80,
                weight=self.weights[ScoreCategoryName.LICENSE],
                details="License file found but type not detected by GitHub.",
            )
        else:
            return ScoreCategory(
                score=0,
                weight=self.weights[ScoreCategoryName.LICENSE],
                details="No license detected — potential legal risk for contributors.",
            )

    def score_documentation(
        self, repo_info: RepoInfo, file_paths: List[str]
    ) -> ScoreCategory:
        """Score documentation quality and presence.

        Checks for:
        - docs/ directory (+30)
        - CONTRIBUTING.md (+25)
        - CODE_OF_CONDUCT.md (+15)
        - CHANGELOG.md (+15)
        - Wiki enabled (+15)

        Args:
            repo_info: Repository metadata.
            file_paths: List of file paths in the repository.

        Returns:
            ScoreCategory with score and details.
        """
        score = 0
        findings: list[str] = []
        lower_paths = [p.lower() for p in file_paths]

        # docs/ directory
        has_docs = any(
            p.startswith("docs/") or p.startswith("doc/") or p == "docs" or p == "doc"
            for p in lower_paths
        )
        if has_docs:
            score += 30
            findings.append("Documentation directory found")
        else:
            findings.append("No docs/ directory")

        # CONTRIBUTING.md
        has_contributing = any(
            p in ("contributing.md", "contributing.rst", "contributing")
            for p in lower_paths
        )
        if has_contributing:
            score += 25
            findings.append("CONTRIBUTING guide present")
        else:
            findings.append("No CONTRIBUTING.md")

        # CODE_OF_CONDUCT.md
        has_coc = any(
            p in ("code_of_conduct.md", "code-of-conduct.md")
            for p in lower_paths
        )
        if has_coc:
            score += 15
            findings.append("Code of Conduct present")
        else:
            findings.append("No Code of Conduct")

        # CHANGELOG.md
        has_changelog = any(
            p in ("changelog.md", "changelog", "changelog.rst", "changes.md", "history.md")
            for p in lower_paths
        )
        if has_changelog:
            score += 15
            findings.append("Changelog maintained")
        else:
            findings.append("No CHANGELOG")

        # Wiki
        if repo_info.has_wiki:
            score += 15
            findings.append("Wiki is enabled")

        return ScoreCategory(
            score=min(score, 100),
            weight=self.weights[ScoreCategoryName.DOCUMENTATION],
            details="; ".join(findings),
        )

    def score_ci_setup(self, file_paths: List[str]) -> ScoreCategory:
        """Score CI/CD setup presence.

        Checks for:
        - GitHub Actions (.github/workflows/)
        - Travis CI (.travis.yml)
        - CircleCI (.circleci/)
        - Jenkins (Jenkinsfile)
        - GitLab CI (.gitlab-ci.yml)
        - Azure Pipelines (azure-pipelines.yml)

        Args:
            file_paths: List of file paths in the repository.

        Returns:
            ScoreCategory with score and details.
        """
        score = 0
        findings: list[str] = []
        lower_paths = [p.lower() for p in file_paths]

        ci_systems = {
            "GitHub Actions": lambda paths: any(
                p.startswith(".github/workflows/") or p in (".github/ci.yml", ".github/workflows-ci.yml", "ci.yml") for p in paths
            ),
            "Travis CI": lambda paths: ".travis.yml" in paths,
            "CircleCI": lambda paths: any(
                p.startswith(".circleci/") for p in paths
            ),
            "Jenkins": lambda paths: "jenkinsfile" in paths,
            "GitLab CI": lambda paths: ".gitlab-ci.yml" in paths,
            "Azure Pipelines": lambda paths: "azure-pipelines.yml" in paths,
        }

        found_systems: list[str] = []
        for name, checker in ci_systems.items():
            if checker(lower_paths):
                found_systems.append(name)

        if found_systems:
            # 50 points for first CI system, 25 for each additional (capped at 100)
            score = min(50 + 25 * (len(found_systems) - 1), 100)
            findings.append(f"CI/CD configured: {', '.join(found_systems)}")
        else:
            findings.append("No CI/CD configuration detected")

        return ScoreCategory(
            score=score,
            weight=self.weights[ScoreCategoryName.CI_SETUP],
            details="; ".join(findings),
        )
