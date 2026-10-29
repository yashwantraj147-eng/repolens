"""Tests for URL validation and parsing utilities."""

import pytest

from app.utils.validators import parse_github_url, validate_repo_identifier


class TestParseGitHubUrl:
    """Tests for parse_github_url function."""

    def test_valid_https_url(self) -> None:
        """Standard HTTPS URL should parse correctly."""
        owner, repo = parse_github_url("https://github.com/fastapi/fastapi")
        assert owner == "fastapi"
        assert repo == "fastapi"

    def test_valid_url_with_www(self) -> None:
        """URL with www prefix should parse correctly."""
        owner, repo = parse_github_url("https://www.github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_with_git_suffix(self) -> None:
        """URL with .git suffix should parse correctly."""
        owner, repo = parse_github_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_with_trailing_path(self) -> None:
        """URL with trailing path segments should parse correctly."""
        owner, repo = parse_github_url("https://github.com/owner/repo/tree/main/src")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_http_url(self) -> None:
        """HTTP (non-HTTPS) URL should parse correctly."""
        owner, repo = parse_github_url("http://github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_without_protocol(self) -> None:
        """URL without protocol should parse correctly."""
        owner, repo = parse_github_url("github.com/owner/repo")
        assert owner == "owner"
        assert repo == "repo"

    def test_valid_url_with_whitespace(self) -> None:
        """URL with surrounding whitespace should be trimmed."""
        owner, repo = parse_github_url("  https://github.com/owner/repo  ")
        assert owner == "owner"
        assert repo == "repo"

    def test_empty_url_raises(self) -> None:
        """Empty string should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_github_url("")

    def test_whitespace_only_raises(self) -> None:
        """Whitespace-only string should raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            parse_github_url("   ")

    def test_non_github_url_raises(self) -> None:
        """Non-GitHub URL should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub"):
            parse_github_url("https://gitlab.com/owner/repo")

    def test_github_profile_url_raises(self) -> None:
        """GitHub profile URL (no repo) should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub"):
            parse_github_url("https://github.com/owner")

    def test_random_string_raises(self) -> None:
        """Random string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub"):
            parse_github_url("not-a-url-at-all")

    def test_reserved_path_raises(self) -> None:
        """GitHub page paths should be rejected."""
        with pytest.raises(ValueError, match="appears to be a GitHub page"):
            parse_github_url("https://github.com/owner/settings")

    def test_hyphenated_names(self) -> None:
        """Hyphenated owner and repo names should parse correctly."""
        owner, repo = parse_github_url("https://github.com/my-org/my-repo")
        assert owner == "my-org"
        assert repo == "my-repo"

    def test_underscored_names(self) -> None:
        """Underscored names should parse correctly."""
        owner, repo = parse_github_url("https://github.com/my_org/my_repo")
        assert owner == "my_org"
        assert repo == "my_repo"

    def test_dotted_names(self) -> None:
        """Dotted names (e.g., v1.0) should parse correctly."""
        owner, repo = parse_github_url("https://github.com/owner/repo.js")
        assert owner == "owner"
        assert repo == "repo.js"


class TestValidateRepoIdentifier:
    """Tests for validate_repo_identifier function."""

    def test_valid_identifiers(self) -> None:
        """Valid owner and repo should not raise."""
        validate_repo_identifier("owner", "repo")

    def test_invalid_owner_raises(self) -> None:
        """Owner with invalid characters should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid GitHub owner"):
            validate_repo_identifier("owner name", "repo")

    def test_invalid_repo_raises(self) -> None:
        """Repo with invalid characters should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid repository name"):
            validate_repo_identifier("owner", "repo name")
