"""Engine for comparing two repository analysis reports head-to-head."""


from app.models.enums import ScoreCategoryName
from app.models.schemas import (
    AnalysisReport,
    CategoryComparison,
    ComparisonMetrics,
    MetricComparison,
)

CATEGORY_NAMES = {
    ScoreCategoryName.README_QUALITY: "README Quality",
    ScoreCategoryName.TEST_PRESENCE: "Test Suite Presence",
    ScoreCategoryName.SECURITY_POSTURE: "Security & Supply Chain",
    ScoreCategoryName.COMMIT_ACTIVITY: "Commit Velocity",
    ScoreCategoryName.DOCUMENTATION: "Documentation & Community",
    ScoreCategoryName.CI_SETUP: "CI/CD Pipeline",
    ScoreCategoryName.ISSUE_RESPONSE_TIME: "Issue Resolution Speed",
    ScoreCategoryName.LICENSE: "Open-Source License",
}


class ComparisonEngine:
    """Calculates head-to-head metrics and produces synthesis verdicts."""

    def compare(
        self, report_a: AnalysisReport, report_b: AnalysisReport
    ) -> ComparisonMetrics:
        """Compare two repository analysis reports.

        Args:
            report_a: Analysis report for repository A.
            report_b: Analysis report for repository B.

        Returns:
            ComparisonMetrics containing winner, score diffs, and synthesized verdict.
        """
        score_a = report_a.health_score.overall
        score_b = report_b.health_score.overall
        score_diff = score_a - score_b

        if score_diff > 0:
            overall_winner = "repo_a"
        elif score_diff < 0:
            overall_winner = "repo_b"
        else:
            overall_winner = "tie"

        # Per-category comparison
        category_comparisons: list[CategoryComparison] = []
        repo_a_wins: list[str] = []
        repo_b_wins: list[str] = []

        for cat_enum, cat_title in CATEGORY_NAMES.items():
            cat_a = report_a.health_score.breakdown.get(cat_enum)
            cat_b = report_b.health_score.breakdown.get(cat_enum)

            sc_a = cat_a.score if cat_a else 0
            sc_b = cat_b.score if cat_b else 0
            diff = sc_a - sc_b

            if diff > 0:
                cat_winner = "repo_a"
                repo_a_wins.append(cat_title)
            elif diff < 0:
                cat_winner = "repo_b"
                repo_b_wins.append(cat_title)
            else:
                cat_winner = "tie"

            category_comparisons.append(
                CategoryComparison(
                    category=cat_enum,
                    name=cat_title,
                    score_a=sc_a,
                    score_b=sc_b,
                    winner=cat_winner,
                    diff=diff,
                    details_a=cat_a.details if cat_a else "No data",
                    details_b=cat_b.details if cat_b else "No data",
                )
            )

        # Community metrics comparison
        stars_diff = report_a.repo.stars - report_b.repo.stars
        forks_diff = report_a.repo.forks - report_b.repo.forks
        issues_diff = report_a.repo.open_issues - report_b.repo.open_issues

        stars_winner = (
            "repo_a" if stars_diff > 0 else "repo_b" if stars_diff < 0 else "tie"
        )
        forks_winner = (
            "repo_a" if forks_diff > 0 else "repo_b" if forks_diff < 0 else "tie"
        )

        metrics = MetricComparison(
            stars_diff=stars_diff,
            forks_diff=forks_diff,
            open_issues_diff=issues_diff,
            stars_winner=stars_winner,
            forks_winner=forks_winner,
        )

        # Build verdict summary
        name_a = f"{report_a.repo.owner}/{report_a.repo.name}"
        name_b = f"{report_b.repo.owner}/{report_b.repo.name}"

        if overall_winner == "repo_a":
            verdict = (
                f"{name_a} takes the lead with an overall score of {score_a}/100 vs {score_b}/100 (+{abs(score_diff)}). "
            )
            if repo_a_wins:
                verdict += f"Key advantages: {', '.join(repo_a_wins[:3])}. "
            if repo_b_wins:
                verdict += f"However, {name_b} demonstrated stronger performance in {', '.join(repo_b_wins[:2])}."
        elif overall_winner == "repo_b":
            verdict = (
                f"{name_b} takes the lead with an overall score of {score_b}/100 vs {score_a}/100 (+{abs(score_diff)}). "
            )
            if repo_b_wins:
                verdict += f"Key advantages: {', '.join(repo_b_wins[:3])}. "
            if repo_a_wins:
                verdict += f"However, {name_a} demonstrated stronger performance in {', '.join(repo_a_wins[:2])}."
        else:
            verdict = (
                f"Both {name_a} and {name_b} are evenly matched with identical health scores of {score_a}/100. "
            )
            if repo_a_wins:
                verdict += f"{name_a} excels in {', '.join(repo_a_wins[:2])}, while {name_b} leads in {', '.join(repo_b_wins[:2])}."

        return ComparisonMetrics(
            overall_winner=overall_winner,
            score_diff=score_diff,
            categories=category_comparisons,
            metrics=metrics,
            verdict_summary=verdict,
        )
