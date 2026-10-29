"""Enumerations used throughout the application."""

from enum import Enum


class ScoreCategoryName(str, Enum):
    """Names of health score categories."""

    README_QUALITY = "readme_quality"
    COMMIT_ACTIVITY = "commit_activity"
    ISSUE_RESPONSE_TIME = "issue_response_time"
    TEST_PRESENCE = "test_presence"
    LICENSE = "license"
    DOCUMENTATION = "documentation"
    CI_SETUP = "ci_setup"


class AnalysisStatus(str, Enum):
    """Status of an analysis job."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
