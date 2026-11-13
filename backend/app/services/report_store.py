"""Persistent SQLite storage and cache for analysis reports.

Provides persistent caching across server restarts, fast retrieval by UUID,
lookup by repository name with TTL expiration, and recent report queries.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from app.models.schemas import AnalysisReport, RecentReportItem

logger = logging.getLogger(__name__)


class ReportStore:
    """Thread-safe SQLite persistent store for repository analysis reports."""

    def __init__(self, db_path: str = "repolens.db") -> None:
        """Initialize the report store and set up database schema.

        Args:
            db_path: Path to the SQLite database file, or ':memory:'.
        """
        self.db_path = db_path
        if db_path != ":memory:":
            db_file = Path(db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)
            self._mem_conn: Optional[sqlite3.Connection] = None
        else:
            # Persistent connection for in-memory DB so tables persist across operations
            self._mem_conn = sqlite3.connect(":memory:", check_same_thread=False, timeout=10.0)
            self._mem_conn.row_factory = sqlite3.Row

        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding a connection and safely closing it upon completion.

        Yields:
            Active sqlite3.Connection with row_factory set to sqlite3.Row.
        """
        if self._mem_conn is not None:
            yield self._mem_conn
            return

        conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create the reports table and indexes if they do not exist."""
        with self._connection() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    repo_key TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    stars INTEGER NOT NULL DEFAULT 0,
                    language TEXT,
                    overall_score INTEGER NOT NULL,
                    grade TEXT NOT NULL,
                    report_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_reports_repo_key ON reports (repo_key, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports (created_at DESC);
                """
            )

    @staticmethod
    def _make_repo_key(owner: str, repo: str) -> str:
        """Generate a canonical lowercase lookup key for a repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Formatted 'owner/repo' key.
        """
        return f"{owner.strip().lower()}/{repo.strip().lower()}"

    def save(self, report: AnalysisReport) -> None:
        """Save or update an analysis report in persistent storage.

        Args:
            report: AnalysisReport instance to persist.
        """
        repo_key = self._make_repo_key(report.repo.owner, report.repo.name)
        report_json = report.model_dump_json()
        created_at_iso = report.generated_at.isoformat()

        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO reports (
                    report_id, repo_key, owner, name, url, stars,
                    language, overall_score, grade, report_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report.report_id,
                    repo_key,
                    report.repo.owner,
                    report.repo.name,
                    report.repo.url,
                    report.repo.stars,
                    report.repo.language,
                    report.health_score.overall,
                    report.health_score.grade,
                    report_json,
                    created_at_iso,
                ),
            )
        logger.debug("Persisted report %s for %s", report.report_id, repo_key)

    def get_by_id(self, report_id: str) -> Optional[AnalysisReport]:
        """Retrieve a report by its unique UUID identifier.

        Args:
            report_id: Unique UUID string.

        Returns:
            AnalysisReport if found, None otherwise.
        """
        with self._connection() as conn:
            row = conn.execute(
                "SELECT report_json FROM reports WHERE report_id = ?",
                (report_id,),
            ).fetchone()

        if not row:
            return None

        try:
            return AnalysisReport.model_validate_json(row["report_json"])
        except Exception as e:
            logger.error("Failed to deserialize report %s: %s", report_id, str(e))
            return None

    def get_latest_for_repo(
        self,
        owner: str,
        repo: str,
        max_age_seconds: Optional[int] = None,
    ) -> Optional[AnalysisReport]:
        """Fetch the most recent report for a repo if it is within TTL.

        Args:
            owner: Repository owner.
            repo: Repository name.
            max_age_seconds: Maximum age in seconds before considering stale.

        Returns:
            Cached AnalysisReport if found and fresh; otherwise None.
        """
        repo_key = self._make_repo_key(owner, repo)
        with self._connection() as conn:
            row = conn.execute(
                """
                SELECT report_json, created_at FROM reports
                WHERE repo_key = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (repo_key,),
            ).fetchone()

        if not row:
            return None

        # Check TTL expiration
        if max_age_seconds is not None and max_age_seconds > 0:
            try:
                created_dt = datetime.fromisoformat(row["created_at"])
                if created_dt.tzinfo is None:
                    created_dt = created_dt.replace(tzinfo=timezone.utc)
                age = (datetime.now(timezone.utc) - created_dt).total_seconds()
                if age > max_age_seconds:
                    logger.debug("Report for %s expired (age %.1fs > %ds)", repo_key, age, max_age_seconds)
                    return None
            except Exception as e:
                logger.warning("Error checking report age: %s", str(e))

        try:
            return AnalysisReport.model_validate_json(row["report_json"])
        except Exception as e:
            logger.error("Failed to deserialize report for %s: %s", repo_key, str(e))
            return None

    def get_recent(self, limit: int = 10) -> List[RecentReportItem]:
        """Retrieve a list of the most recently analyzed repositories.

        Args:
            limit: Maximum items to return (default 10).

        Returns:
            List of RecentReportItem summaries.
        """
        with self._connection() as conn:
            rows = conn.execute(
                """
                SELECT report_id, owner, name, url, stars, language,
                       overall_score, grade, created_at
                FROM reports
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        items = []
        for r in rows:
            try:
                gen_at = datetime.fromisoformat(r["created_at"])
                items.append(
                    RecentReportItem(
                        report_id=r["report_id"],
                        owner=r["owner"],
                        name=r["name"],
                        url=r["url"],
                        stars=r["stars"],
                        language=r["language"],
                        overall_score=r["overall_score"],
                        grade=r["grade"],
                        generated_at=gen_at,
                    )
                )
            except Exception as e:
                logger.warning("Error mapping recent report row: %s", str(e))
        return items

    def delete_by_id(self, report_id: str) -> bool:
        """Delete a report by its UUID identifier.

        Args:
            report_id: Unique report identifier.

        Returns:
            True if row was deleted, False if not found.
        """
        with self._connection() as conn:
            cursor = conn.execute("DELETE FROM reports WHERE report_id = ?", (report_id,))
            return cursor.rowcount > 0

    def count(self) -> int:
        """Return the total number of stored reports."""
        with self._connection() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM reports").fetchone()
            return row["cnt"] if row else 0


# Global singleton instance
_store_instance: Optional[ReportStore] = None


def get_report_store(db_path: Optional[str] = None) -> ReportStore:
    """Get or create the global ReportStore singleton instance.

    Args:
        db_path: Optional custom database path.

    Returns:
        ReportStore instance.
    """
    global _store_instance
    if _store_instance is None:
        if db_path is None:
            from app.config import get_settings
            db_path = get_settings().db_path
        _store_instance = ReportStore(db_path=db_path)
    return _store_instance
