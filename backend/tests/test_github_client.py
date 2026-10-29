"""Tests for the GitHub API client."""

import pytest
import respx
import httpx

from app.config import Settings
from app.services.github_client import (
    GitHubClient,
    RepoNotFoundError,
    RateLimitExceededError,
    GitHubClientError,
)


@pytest.fixture
def settings() -> Settings:
    """Create test settings."""
    return Settings(
        github_token="test-token",
        github_api_base="https://api.github.com",
    )


@pytest.fixture
def github_client(settings: Settings) -> GitHubClient:
    """Create a GitHubClient instance for testing."""
    return GitHubClient(settings)


class TestGitHubClient:
    """Tests for GitHubClient."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_repo_info_success(
        self, github_client: GitHubClient, sample_repo_data: dict
    ) -> None:
        """Successful repo info fetch should return RepoInfo."""
        respx.get("https://api.github.com/repos/fastapi/fastapi").mock(
            return_value=httpx.Response(200, json=sample_repo_data)
        )
        repo_info = await github_client.get_repo_info("fastapi", "fastapi")
        assert repo_info.owner == "fastapi"
        assert repo_info.name == "fastapi"
        assert repo_info.stars == 75000

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_repo_info_not_found(
        self, github_client: GitHubClient
    ) -> None:
        """404 response should raise RepoNotFoundError."""
        respx.get("https://api.github.com/repos/owner/nonexistent").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )
        with pytest.raises(RepoNotFoundError):
            await github_client.get_repo_info("owner", "nonexistent")

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_readme_success(
        self, github_client: GitHubClient
    ) -> None:
        """Successful README fetch should return content string."""
        respx.get("https://api.github.com/repos/owner/repo/readme").mock(
            return_value=httpx.Response(200, text="# My Repo\nHello world")
        )
        readme = await github_client.get_readme("owner", "repo")
        assert readme is not None
        assert "My Repo" in readme

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_readme_not_found(
        self, github_client: GitHubClient
    ) -> None:
        """Missing README should return None."""
        respx.get("https://api.github.com/repos/owner/repo/readme").mock(
            return_value=httpx.Response(404, json={"message": "Not Found"})
        )
        readme = await github_client.get_readme("owner", "repo")
        assert readme is None

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_file_tree(
        self, github_client: GitHubClient, sample_tree_data: dict
    ) -> None:
        """File tree fetch should return filtered entries."""
        respx.get("https://api.github.com/repos/owner/repo/git/trees/HEAD").mock(
            return_value=httpx.Response(200, json=sample_tree_data)
        )
        tree = await github_client.get_file_tree("owner", "repo")
        assert len(tree) > 0
        paths = [entry["path"] for entry in tree]
        assert "README.md" in paths

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_recent_commits(
        self, github_client: GitHubClient
    ) -> None:
        """Recent commits fetch should return a list."""
        commits = [
            {"sha": "abc123", "commit": {"message": "feat: init"}},
            {"sha": "def456", "commit": {"message": "fix: bug"}},
        ]
        respx.get("https://api.github.com/repos/owner/repo/commits").mock(
            return_value=httpx.Response(200, json=commits)
        )
        result = await github_client.get_recent_commits("owner", "repo")
        assert len(result) == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_languages(
        self, github_client: GitHubClient
    ) -> None:
        """Languages fetch should return dict."""
        respx.get("https://api.github.com/repos/owner/repo/languages").mock(
            return_value=httpx.Response(200, json={"Python": 50000, "JavaScript": 10000})
        )
        languages = await github_client.get_languages("owner", "repo")
        assert "Python" in languages
        assert languages["Python"] == 50000

    @respx.mock
    @pytest.mark.asyncio
    async def test_rate_limit_headers_tracked(
        self, github_client: GitHubClient, sample_repo_data: dict
    ) -> None:
        """Rate limit headers should be tracked after requests."""
        respx.get("https://api.github.com/repos/owner/repo").mock(
            return_value=httpx.Response(
                200,
                json=sample_repo_data,
                headers={
                    "x-ratelimit-remaining": "4999",
                    "x-ratelimit-limit": "5000",
                    "x-ratelimit-reset": "1700000000",
                },
            )
        )
        await github_client.get_repo_info("owner", "repo")
        assert github_client.rate_limiter.state.remaining == 4999
