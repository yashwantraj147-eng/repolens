"""Input validation helpers for GitHub URLs and repository identifiers."""

import re
from typing import Tuple


# Matches github.com/owner/repo with optional trailing segments
GITHUB_URL_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?github\.com/(?P<owner>[a-zA-Z0-9\-_.]+)/(?P<repo>[a-zA-Z0-9\-_.]+?)(?:\.git)?(?:/.*)?$"
)


def parse_github_url(url: str) -> Tuple[str, str]:
    """Parse a GitHub URL and extract owner and repository name.

    Args:
        url: A GitHub repository URL (e.g., "https://github.com/owner/repo").

    Returns:
        A tuple of (owner, repo_name).

    Raises:
        ValueError: If the URL is not a valid GitHub repository URL.
    """
    url = url.strip()
    if not url:
        raise ValueError("Repository URL cannot be empty")

    match = GITHUB_URL_PATTERN.match(url)
    if not match:
        raise ValueError(
            f"Invalid GitHub repository URL: '{url}'. "
            "Expected format: https://github.com/owner/repo"
        )

    owner = match.group("owner")
    repo = match.group("repo")

    # Reject URLs that point to GitHub pages rather than repos
    reserved_paths = {"settings", "pulls", "issues", "actions", "wiki", "security", "pulse", "community"}
    if repo.lower() in reserved_paths:
        raise ValueError(
            f"'{url}' appears to be a GitHub page, not a repository URL. "
            "Please provide the repository root URL."
        )

    return owner, repo


def validate_repo_identifier(owner: str, repo: str) -> None:
    """Validate that owner and repo names are well-formed.

    Args:
        owner: GitHub username or organization name.
        repo: Repository name.

    Raises:
        ValueError: If either identifier is invalid.
    """
    if not re.match(r"^[a-zA-Z0-9\-_.]+$", owner):
        raise ValueError(f"Invalid GitHub owner name: '{owner}'")
    if not re.match(r"^[a-zA-Z0-9\-_.]+$", repo):
        raise ValueError(f"Invalid repository name: '{repo}'")
