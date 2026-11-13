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
    """Tests for the /api/reports/{report_id} and /api/reports/recent endpoints."""

    def test_nonexistent_report_returns_404(self, client: TestClient) -> None:
        """Requesting a non-existent report should return 404."""
        response = client.get("/api/reports/nonexistent-id")
        assert response.status_code == 404

    def test_report_not_found_message(self, client: TestClient) -> None:
        """404 response should include a helpful message."""
        response = client.get("/api/reports/fake-id")
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_get_recent_reports_empty_or_populated(self, client: TestClient) -> None:
        """Recent reports endpoint should return a list."""
        response = client.get("/api/reports/recent")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_persisted_report_by_id(self, client: TestClient) -> None:
        """Report stored in report store should be retrievable via GET /api/reports/{id}."""
        from tests.test_report_store import create_sample_report
        from app.services.report_store import get_report_store

        store = get_report_store()
        sample = create_sample_report(owner="persisted-owner", name="persisted-repo", score=88)
        store.save(sample)

        response = client.get(f"/api/reports/{sample.report_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["report_id"] == sample.report_id
        assert data["repo"]["owner"] == "persisted-owner"
        assert data["health_score"]["overall"] == 88
