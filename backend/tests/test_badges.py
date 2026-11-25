"""Tests for the dynamic SVG badge generator and router."""

from fastapi.testclient import TestClient

from app.services.badge_generator import generate_badge_svg, get_grade_color
from app.services.report_store import get_report_store
from tests.test_report_store import create_sample_report


class TestBadgeGenerator:
    """Test suite for SVG badge generation."""

    def test_grade_colors(self) -> None:
        """Grades should map to accessible GitHub status colors."""
        assert get_grade_color("A+") == "#2ea44f"
        assert get_grade_color("A") == "#2ea44f"
        assert get_grade_color("B+") == "#0969da"
        assert get_grade_color("B") == "#0969da"
        assert get_grade_color("C+") == "#8250df"
        assert get_grade_color("C") == "#d29922"
        assert get_grade_color("D") == "#cf222e"
        assert get_grade_color("F") == "#cf222e"
        assert get_grade_color("unknown") == "#6e7681"

    def test_generate_badge_svg_structure(self) -> None:
        """Badge should output valid, accessible SVG XML markup."""
        svg = generate_badge_svg(label="repolens", value="92/100 · A+", grade="A+", style="flat")
        assert svg.startswith("<svg")
        assert svg.endswith("</svg>")
        assert 'role="img"' in svg
        assert "repolens" in svg
        assert "92/100 · A+" in svg
        assert "#2ea44f" in svg

    def test_badge_styles(self) -> None:
        """Styles should adjust corners and dimensions."""
        flat = generate_badge_svg(style="flat")
        assert 'rx="3"' in flat

        square = generate_badge_svg(style="flat-square")
        assert 'rx="0"' in square

        badge_bold = generate_badge_svg(style="for-the-badge")
        assert 'height="28"' in badge_bold


class TestBadgeEndpoints:
    """Test suite for badge API endpoints."""

    def test_get_badge_by_id_success(self, client: TestClient) -> None:
        """Existing report should return a valid SVG badge with 200 OK."""
        store = get_report_store()
        report = create_sample_report(owner="badge-owner", name="badge-repo", score=94)
        store.save(report)

        response = client.get(f"/api/badge/id/{report.report_id}.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "94/100" in response.text
        assert "repolens" in response.text

    def test_get_badge_by_id_not_found(self, client: TestClient) -> None:
        """Non-existent report should return a graceful 'not found' SVG badge."""
        response = client.get("/api/badge/id/nonexistent-uuid.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "not found" in response.text

    def test_get_repo_badge_cached(self, client: TestClient) -> None:
        """Cached repository badge should return score and grade immediately."""
        store = get_report_store()
        report = create_sample_report(owner="octocat", name="spoon-knife", score=88)
        store.save(report)

        response = client.get("/api/badge/octocat/spoon-knife.svg?metric=grade")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]
        assert "Grade" in response.text

    def test_get_repo_badge_styles(self, client: TestClient) -> None:
        """Badge endpoint should support style query parameters."""
        store = get_report_store()
        report = create_sample_report(owner="octocat", name="hello-world", score=76)
        store.save(report)

        response = client.get("/api/badge/octocat/hello-world.svg?style=for-the-badge")
        assert response.status_code == 200
        assert 'height="28"' in response.text

