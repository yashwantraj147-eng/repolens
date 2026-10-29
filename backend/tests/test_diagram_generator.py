"""Tests for the architecture diagram generator and onboarding / summary generators."""

import pytest
from datetime import datetime, timezone

from app.config import Settings
from app.models.schemas import RepoInfo
from app.services.diagram_generator import DiagramGenerator
from app.services.onboarding_guide import OnboardingGuideGenerator
from app.services.summary_generator import SummaryGenerator


@pytest.fixture
def sample_repo() -> RepoInfo:
    return RepoInfo(
        owner="testorg",
        name="testproject",
        url="https://github.com/testorg/testproject",
        description="A full-stack application for automated repo analysis",
        language="TypeScript",
        stars=1500,
        forks=120,
        open_issues=15,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        default_branch="main",
        topics=["fastapi", "react", "analysis"],
        has_wiki=True,
        license_name="MIT",
        size=2048,
    )


class TestDiagramGenerator:
    """Tests for Mermaid architecture diagram generation."""

    def test_fullstack_project_detection(self, sample_repo: RepoInfo) -> None:
        generator = DiagramGenerator()
        file_tree = [
            {"path": "package.json", "type": "blob"},
            {"path": "src/App.tsx", "type": "blob"},
            {"path": "backend/requirements.txt", "type": "blob"},
            {"path": "backend/routers/api.py", "type": "blob"},
            {"path": "docker-compose.yml", "type": "blob"},
            {"path": ".github/workflows/ci.yml", "type": "blob"},
        ]
        languages = {"TypeScript": 60000, "Python": 40000}

        mermaid = generator.generate(sample_repo, file_tree, languages)

        assert "graph TD" in mermaid
        assert "ROOT[" in mermaid
        assert "TypeScript" in mermaid or "Multi-language" in mermaid
        assert "INFRA" in mermaid

    def test_sanitize_id(self) -> None:
        generator = DiagramGenerator()
        assert generator._sanitize_id("my-service.v1") == "MY_SERVICE_V1"
        assert generator._sanitize_id("123abc") == "D_123ABC"

    def test_empty_file_tree(self, sample_repo: RepoInfo) -> None:
        generator = DiagramGenerator()
        mermaid = generator.generate(sample_repo, [], {})
        assert "graph TD" in mermaid
        assert "ROOT[" in mermaid


class TestSummaryGenerator:
    """Tests for summary generation."""

    @pytest.mark.asyncio
    async def test_template_summary_generation(self, sample_repo: RepoInfo) -> None:
        settings = Settings(openai_api_key=None)
        generator = SummaryGenerator(settings)

        file_tree = [
            {"path": "src/index.ts", "type": "blob"},
            {"path": "tests/test_core.py", "type": "blob"},
            {"path": "Dockerfile", "type": "blob"},
        ]
        languages = {"TypeScript": 80000, "Python": 20000}

        summary = await generator.generate(sample_repo, None, languages, file_tree)

        assert "testorg/testproject" in summary
        assert "1,500 stars" in summary
        assert "TypeScript" in summary


class TestOnboardingGuideGenerator:
    """Tests for onboarding guide generation."""

    @pytest.mark.asyncio
    async def test_guide_structure(self, sample_repo: RepoInfo) -> None:
        settings = Settings(openai_api_key=None)
        generator = OnboardingGuideGenerator(settings)

        file_tree = [
            {"path": "package.json", "type": "blob"},
            {"path": "yarn.lock", "type": "blob"},
            {"path": "vitest.config.ts", "type": "blob"},
            {"path": ".env.example", "type": "blob"},
        ]
        languages = {"TypeScript": 100000}

        guide = await generator.generate(sample_repo, None, file_tree, languages)

        assert "## Getting Started with testorg/testproject" in guide
        assert "Prerequisites" in guide
        assert "yarn install" in guide
        assert "npx vitest" in guide
        assert "cp .env.example .env" in guide

