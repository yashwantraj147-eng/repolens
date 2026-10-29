"""GitHub REST API client with rate limiting and error handling."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import Settings
from app.models.schemas import RepoInfo
from app.utils.rate_limiter import RateLimitHandler
from app.utils.validators import parse_github_url

logger = logging.getLogger(__name__)


class GitHubClientError(Exception):
    """Base exception for GitHub client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class RepoNotFoundError(GitHubClientError):
    """Raised when a repository is not found or is private."""
    pass


class RateLimitExceededError(GitHubClientError):
    """Raised when GitHub API rate limit is exceeded."""
    pass


class GitHubClient:
    """Async client for the GitHub REST API.

    Provides methods to fetch repository metadata, file trees,
    commit history, issues, and more. Handles rate limiting
    with exponential backoff.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the GitHub client.

        Args:
            settings: Application settings containing GitHub token and API base URL.
        """
        self.base_url = settings.github_api_base.rstrip("/")
        self.token = settings.github_token
        self.rate_limiter = RateLimitHandler()
        self._headers = self._build_headers()

    def _build_headers(self) -> Dict[str, str]:
        """Build HTTP headers for GitHub API requests.

        Returns:
            Dictionary of HTTP headers.
        """
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "RepoLens/1.0",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Make an authenticated request to the GitHub API.

        Handles rate limiting, retries, and error responses.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (e.g., "/repos/owner/repo").
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            RepoNotFoundError: If the repo is not found (404).
            RateLimitExceededError: If rate limit is exhausted after retries.
            GitHubClientError: For other API errors.
        """
        url = f"{self.base_url}{path}"

        for attempt in range(self.rate_limiter.max_retries + 1):
            await self.rate_limiter.wait_if_needed()

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method, url, headers=self._headers, params=params
                )

            self.rate_limiter.update_from_response(response)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise RepoNotFoundError(
                    "Repository not found. It may be private or the URL may be incorrect.",
                    status_code=404,
                )
            elif self.rate_limiter.is_rate_limited(response):
                if attempt < self.rate_limiter.max_retries:
                    delay = await self.rate_limiter.get_backoff_delay(attempt)
                    logger.warning(
                        "Rate limited. Retrying in %.1f seconds (attempt %d/%d).",
                        delay,
                        attempt + 1,
                        self.rate_limiter.max_retries,
                    )
                    import asyncio
                    await asyncio.sleep(delay)
                    continue
                raise RateLimitExceededError(
                    "GitHub API rate limit exceeded. Please try again later or provide a GITHUB_TOKEN.",
                    status_code=429,
                )
            else:
                raise GitHubClientError(
                    f"GitHub API error: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                )

        raise GitHubClientError("Maximum retries exceeded")

    async def get_repo_info(self, owner: str, repo: str) -> RepoInfo:
        """Fetch basic repository information.

        Args:
            owner: Repository owner/organization.
            repo: Repository name.

        Returns:
            RepoInfo model with repository metadata.
        """
        data = await self._request("GET", f"/repos/{owner}/{repo}")

        return RepoInfo(
            owner=data["owner"]["login"],
            name=data["name"],
            url=data["html_url"],
            description=data.get("description"),
            language=data.get("language"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            default_branch=data.get("default_branch", "main"),
            topics=data.get("topics", []),
            has_wiki=data.get("has_wiki", False),
            license_name=data.get("license", {}).get("spdx_id") if data.get("license") else None,
            size=data.get("size", 0),
        )

    async def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """Fetch the repository README content.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            README content as a string, or None if not found.
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/readme",
                    headers={**self._headers, "Accept": "application/vnd.github.raw+json"},
                )
            self.rate_limiter.update_from_response(response)
            if response.status_code == 200:
                return response.text
            return None
        except Exception:
            return None

    async def get_file_tree(
        self, owner: str, repo: str, max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """Fetch the repository file tree (recursive, limited depth).

        Args:
            owner: Repository owner.
            repo: Repository name.
            max_depth: Maximum directory depth to traverse.

        Returns:
            List of tree entry dicts with 'path', 'type', and 'size'.
        """
        try:
            data = await self._request(
                "GET",
                f"/repos/{owner}/{repo}/git/trees/HEAD",
                params={"recursive": "1"},
            )
            entries = data.get("tree", [])

            # Filter by depth
            filtered = []
            for entry in entries:
                depth = entry["path"].count("/")
                if depth < max_depth:
                    filtered.append({
                        "path": entry["path"],
                        "type": entry["type"],
                        "size": entry.get("size", 0),
                    })

            return filtered
        except GitHubClientError:
            return []

    async def get_recent_commits(
        self, owner: str, repo: str, days: int = 90, per_page: int = 100
    ) -> List[Dict[str, Any]]:
        """Fetch recent commits within a time window.

        Args:
            owner: Repository owner.
            repo: Repository name.
            days: Number of days to look back.
            per_page: Maximum commits per page.

        Returns:
            List of commit data dicts.
        """
        since = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        from datetime import timedelta
        since = since - timedelta(days=days)

        try:
            data = await self._request(
                "GET",
                f"/repos/{owner}/{repo}/commits",
                params={
                    "since": since.isoformat(),
                    "per_page": min(per_page, 100),
                },
            )
            return data if isinstance(data, list) else []
        except GitHubClientError:
            return []

    async def get_closed_issues(
        self, owner: str, repo: str, per_page: int = 20
    ) -> List[Dict[str, Any]]:
        """Fetch recently closed issues for response time analysis.

        Args:
            owner: Repository owner.
            repo: Repository name.
            per_page: Number of issues to fetch.

        Returns:
            List of issue data dicts.
        """
        try:
            data = await self._request(
                "GET",
                f"/repos/{owner}/{repo}/issues",
                params={
                    "state": "closed",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": min(per_page, 100),
                },
            )
            # Filter out pull requests (they also appear in the issues endpoint)
            return [
                issue for issue in (data if isinstance(data, list) else [])
                if "pull_request" not in issue
            ]
        except GitHubClientError:
            return []

    async def get_issue_comments(
        self, owner: str, repo: str, issue_number: int
    ) -> List[Dict[str, Any]]:
        """Fetch comments for a specific issue.

        Args:
            owner: Repository owner.
            repo: Repository name.
            issue_number: Issue number.

        Returns:
            List of comment data dicts.
        """
        try:
            data = await self._request(
                "GET",
                f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
                params={"per_page": 5},
            )
            return data if isinstance(data, list) else []
        except GitHubClientError:
            return []

    async def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch language breakdown for the repository.

        Args:
            owner: Repository owner.
            repo: Repository name.

        Returns:
            Dict mapping language names to bytes of code.
        """
        try:
            data = await self._request("GET", f"/repos/{owner}/{repo}/languages")
            return data if isinstance(data, dict) else {}
        except GitHubClientError:
            return {}

    async def get_contents(
        self, owner: str, repo: str, path: str = ""
    ) -> List[Dict[str, Any]]:
        """Fetch directory contents at a specific path.

        Args:
            owner: Repository owner.
            repo: Repository name.
            path: Path within the repository.

        Returns:
            List of content entry dicts.
        """
        try:
            data = await self._request(
                "GET", f"/repos/{owner}/{repo}/contents/{path}"
            )
            return data if isinstance(data, list) else []
        except GitHubClientError:
            return []
