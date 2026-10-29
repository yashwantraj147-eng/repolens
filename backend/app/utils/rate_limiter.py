"""GitHub API rate limit handler with exponential backoff."""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """Tracks GitHub API rate limit state."""

    remaining: int = 5000
    limit: int = 5000
    reset_timestamp: float = 0.0
    last_checked: float = field(default_factory=time.time)

    @property
    def is_exhausted(self) -> bool:
        """Check if rate limit is exhausted."""
        return self.remaining <= 0 and time.time() < self.reset_timestamp

    @property
    def seconds_until_reset(self) -> float:
        """Seconds until the rate limit resets."""
        return max(0, self.reset_timestamp - time.time())

    def update_from_headers(self, headers: httpx.Headers) -> None:
        """Update rate limit state from GitHub response headers.

        Args:
            headers: HTTP response headers containing rate limit info.
        """
        if "x-ratelimit-remaining" in headers:
            self.remaining = int(headers["x-ratelimit-remaining"])
        if "x-ratelimit-limit" in headers:
            self.limit = int(headers["x-ratelimit-limit"])
        if "x-ratelimit-reset" in headers:
            self.reset_timestamp = float(headers["x-ratelimit-reset"])
        self.last_checked = time.time()


class RateLimitHandler:
    """Handles GitHub API rate limiting with exponential backoff.

    Provides middleware-like functionality to check rate limits before
    making requests and handle 403/429 responses gracefully.
    """

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0) -> None:
        """Initialize the rate limit handler.

        Args:
            max_retries: Maximum number of retry attempts.
            base_delay: Base delay in seconds for exponential backoff.
        """
        self.state = RateLimitState()
        self.max_retries = max_retries
        self.base_delay = base_delay

    async def wait_if_needed(self) -> None:
        """Wait if rate limit is exhausted.

        Blocks until the rate limit resets if we've hit the limit.
        """
        if self.state.is_exhausted:
            wait_time = self.state.seconds_until_reset + 1  # +1s buffer
            logger.warning(
                "GitHub rate limit exhausted. Waiting %.1f seconds until reset.",
                wait_time,
            )
            await asyncio.sleep(wait_time)

    def update_from_response(self, response: httpx.Response) -> None:
        """Update rate limit state from a GitHub API response.

        Args:
            response: The HTTP response from GitHub.
        """
        self.state.update_from_headers(response.headers)

        if self.state.remaining <= 10:
            logger.warning(
                "GitHub rate limit low: %d/%d remaining. Resets in %.0f seconds.",
                self.state.remaining,
                self.state.limit,
                self.state.seconds_until_reset,
            )

    def is_rate_limited(self, response: httpx.Response) -> bool:
        """Check if a response indicates rate limiting.

        Args:
            response: The HTTP response to check.

        Returns:
            True if the response is a rate limit error.
        """
        return response.status_code in (403, 429) and "rate limit" in response.text.lower()

    async def get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay.

        Args:
            attempt: The current retry attempt number (0-indexed).

        Returns:
            The delay in seconds before the next retry.
        """
        delay = self.base_delay * (2 ** attempt)
        return min(delay, 60.0)  # Cap at 60 seconds

    def get_status_summary(self) -> str:
        """Get a human-readable summary of the rate limit status.

        Returns:
            A string describing the current rate limit state.
        """
        return (
            f"Rate limit: {self.state.remaining}/{self.state.limit} remaining, "
            f"resets in {self.state.seconds_until_reset:.0f}s"
        )
