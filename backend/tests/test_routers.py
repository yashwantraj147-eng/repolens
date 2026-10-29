"""Tests for API router endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint should return 200 with status info."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_body(self, client: TestClient) -> None:
        """Health endpoint should return expected fields."""
        response = client.get("/api/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "RepoLens"
        assert "version" in data


class TestAnalyzeEndpoint:
    """Tests for the /api/analyze endpoint."""

    def test_invalid_url_returns_422(self, client: TestClient) -> None:
        """Invalid URL format should return 422."""
        response = client.post("/api/analyze", json={"repo_url": "not-a-url"})
        assert response.status_code == 422

    def test_missing_url_returns_422(self, client: TestClient) -> None:
        """Missing repo_url field should return 422."""
        response = client.post("/api/analyze", json={})
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client: TestClient) -> None:
        """Empty request body should return 422."""
        response = client.post("/api/analyze")
        assert response.status_code == 422


class TestReportsEndpoint:
    """Tests for the /api/reports/{report_id} endpoint."""

    def test_nonexistent_report_returns_404(self, client: TestClient) -> None:
        """Requesting a non-existent report should return 404."""
        response = client.get("/api/reports/nonexistent-id")
        assert response.status_code == 404

    def test_report_not_found_message(self, client: TestClient) -> None:
        """404 response should include a helpful message."""
        response = client.get("/api/reports/fake-id")
        data = response.json()
        assert "not found" in data["detail"].lower()
