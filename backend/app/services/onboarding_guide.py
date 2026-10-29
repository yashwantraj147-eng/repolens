"""Getting Started / Onboarding guide generator.

Produces a contributor-friendly onboarding guide based on
repository structure and metadata.
"""

from typing import Any, Dict, List, Optional

from app.config import Settings
from app.models.schemas import RepoInfo
from app.services.llm.base import LLMProvider
from app.services.llm.local import LocalProvider
from app.services.llm.openai import OpenAIProvider


class OnboardingGuideGenerator:
    """Generates a 'Getting Started' guide for new contributors.

    Analyzes repository structure to produce step-by-step instructions
    for setting up the development environment and making contributions.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the onboarding guide generator.

        Args:
            settings: Application settings for LLM configuration.
        """
        self.settings = settings
        self.llm: LLMProvider = self._create_provider()

    def _create_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider based on settings.

        Returns:
            An LLM provider instance.
        """
        if self.settings.openai_api_key:
            return OpenAIProvider(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url or "https://api.openai.com/v1",
                model=self.settings.llm_model,
            )
        return LocalProvider()

    async def generate(
        self,
        repo_info: RepoInfo,
        readme_content: Optional[str] = None,
        file_tree: Optional[List[Dict[str, Any]]] = None,
        languages: Optional[Dict[str, int]] = None,
    ) -> str:
        """Generate an onboarding guide for the repository.

        Args:
            repo_info: Repository metadata.
            readme_content: Raw README content.
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            Markdown-formatted onboarding guide.
        """
        # Always use template-based generation for consistency
        # LLM can optionally enhance if available
        return self._generate_from_template(
            repo_info, readme_content, file_tree, languages
        )

    def _generate_from_template(
        self,
        repo_info: RepoInfo,
        readme_content: Optional[str],
        file_tree: Optional[List[Dict[str, Any]]],
        languages: Optional[Dict[str, int]],
    ) -> str:
        """Generate onboarding guide using templates and heuristics.

        Args:
            repo_info: Repository metadata.
            readme_content: Raw README content.
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            Markdown-formatted guide string.
        """
        file_tree = file_tree or []
        languages = languages or {}
        sections: list[str] = []

        # Header
        sections.append(f"## Getting Started with {repo_info.owner}/{repo_info.name}\n")
        sections.append(
            f"Welcome! This guide will help you set up your development environment "
            f"and start contributing to **{repo_info.name}**.\n"
        )

        # Prerequisites
        sections.append("### Prerequisites\n")
        prereqs = self._detect_prerequisites(repo_info, file_tree, languages)
        for prereq in prereqs:
            sections.append(f"- {prereq}")
        sections.append("")

        # Clone and setup
        sections.append("### Setup\n")
        sections.append("1. **Fork and clone the repository:**\n")
        sections.append(f"```bash")
        sections.append(f"git clone https://github.com/YOUR_USERNAME/{repo_info.name}.git")
        sections.append(f"cd {repo_info.name}")
        sections.append(f"```\n")

        # Language-specific setup
        setup_steps = self._get_setup_steps(repo_info, file_tree, languages)
        step_num = 2
        for step_title, step_commands in setup_steps:
            sections.append(f"{step_num}. **{step_title}:**\n")
            if step_commands:
                sections.append("```bash")
                for cmd in step_commands:
                    sections.append(cmd)
                sections.append("```\n")
            step_num += 1

        # Project structure
        sections.append("### Project Structure\n")
        structure = self._describe_structure(file_tree)
        sections.append("```")
        for line in structure:
            sections.append(line)
        sections.append("```\n")

        # Running tests
        test_commands = self._get_test_commands(file_tree, languages)
        if test_commands:
            sections.append("### Running Tests\n")
            sections.append("```bash")
            for cmd in test_commands:
                sections.append(cmd)
            sections.append("```\n")

        # Contributing workflow
        sections.append("### Making Your First Contribution\n")
        sections.append("1. Create a new branch: `git checkout -b feature/your-feature`")
        sections.append("2. Make your changes and write tests")
        sections.append("3. Run the test suite to ensure nothing is broken")
        sections.append("4. Commit with a descriptive message: `git commit -m \"feat: add new feature\"`")
        sections.append("5. Push and open a Pull Request\n")

        # Helpful links
        sections.append("### Helpful Links\n")
        sections.append(f"- [Repository]({repo_info.url})")
        sections.append(f"- [Issues]({repo_info.url}/issues)")
        sections.append(f"- [Pull Requests]({repo_info.url}/pulls)")
        if repo_info.has_wiki:
            sections.append(f"- [Wiki]({repo_info.url}/wiki)")
        sections.append("")

        return "\n".join(sections)

    def _detect_prerequisites(
        self,
        repo_info: RepoInfo,
        file_tree: List[Dict[str, Any]],
        languages: Dict[str, int],
    ) -> list[str]:
        """Detect required tools and prerequisites.

        Args:
            repo_info: Repository metadata.
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            List of prerequisite descriptions.
        """
        prereqs = ["Git"]
        paths = {entry["path"].lower() for entry in file_tree}

        # Language-specific prerequisites
        lang = (repo_info.language or "").lower()
        top_langs = set(l.lower() for l in languages.keys())

        if lang == "python" or "python" in top_langs or "requirements.txt" in paths:
            prereqs.append("Python 3.8+ with pip")
        if lang == "javascript" or lang == "typescript" or "javascript" in top_langs:
            if "yarn.lock" in paths:
                prereqs.append("Node.js 18+ with Yarn")
            elif "pnpm-lock.yaml" in paths:
                prereqs.append("Node.js 18+ with pnpm")
            else:
                prereqs.append("Node.js 18+ with npm")
        if lang == "go" or "go" in top_langs:
            prereqs.append("Go 1.21+")
        if lang == "rust" or "rust" in top_langs:
            prereqs.append("Rust (latest stable) with Cargo")
        if lang == "java" or "java" in top_langs:
            if "pom.xml" in paths:
                prereqs.append("Java 17+ with Maven")
            elif any("gradle" in p for p in paths):
                prereqs.append("Java 17+ with Gradle")
            else:
                prereqs.append("Java 17+")
        if lang == "ruby" or "ruby" in top_langs:
            prereqs.append("Ruby 3.0+ with Bundler")

        if any("dockerfile" in p for p in paths):
            prereqs.append("Docker (optional, for containerized setup)")

        return prereqs

    def _get_setup_steps(
        self,
        repo_info: RepoInfo,
        file_tree: List[Dict[str, Any]],
        languages: Dict[str, int],
    ) -> list[tuple[str, list[str]]]:
        """Get language-specific setup steps.

        Args:
            repo_info: Repository metadata.
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            List of (step_title, commands) tuples.
        """
        steps: list[tuple[str, list[str]]] = []
        paths = {entry["path"].lower() for entry in file_tree}
        lang = (repo_info.language or "").lower()

        if lang == "python" or "requirements.txt" in paths:
            steps.append(("Create a virtual environment", [
                "python -m venv venv",
                "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
            ]))
            if "requirements.txt" in paths:
                steps.append(("Install dependencies", ["pip install -r requirements.txt"]))
            elif "pyproject.toml" in paths:
                steps.append(("Install dependencies", ["pip install -e '.[dev]'"]))
            elif "setup.py" in paths:
                steps.append(("Install dependencies", ["pip install -e '.[dev]'"]))

        if "package.json" in paths:
            if "yarn.lock" in paths:
                steps.append(("Install Node.js dependencies", ["yarn install"]))
            elif "pnpm-lock.yaml" in paths:
                steps.append(("Install Node.js dependencies", ["pnpm install"]))
            else:
                steps.append(("Install Node.js dependencies", ["npm install"]))

        if "go.mod" in paths:
            steps.append(("Download Go modules", ["go mod download"]))

        if "cargo.toml" in paths:
            steps.append(("Build the project", ["cargo build"]))

        if "gemfile" in paths:
            steps.append(("Install Ruby gems", ["bundle install"]))

        # Environment setup
        if ".env.example" in paths:
            steps.append(("Set up environment variables", [
                "cp .env.example .env",
                "# Edit .env with your configuration",
            ]))

        return steps

    def _get_test_commands(
        self,
        file_tree: List[Dict[str, Any]],
        languages: Dict[str, int],
    ) -> list[str]:
        """Determine how to run tests for the project.

        Args:
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            List of test commands.
        """
        paths = {entry["path"].lower() for entry in file_tree}
        commands: list[str] = []

        if "pytest.ini" in paths or any(
            p.startswith("tests/") and p.endswith(".py") for p in paths
        ):
            commands.append("pytest")
        elif "setup.cfg" in paths or "pyproject.toml" in paths:
            commands.append("python -m pytest")

        if "jest.config.js" in paths or "jest.config.ts" in paths:
            commands.append("npm test")
        elif "vitest.config.js" in paths or "vitest.config.ts" in paths:
            commands.append("npx vitest")

        if any(p.endswith("_test.go") for p in paths):
            commands.append("go test ./...")

        if "cargo.toml" in paths:
            commands.append("cargo test")

        if not commands:
            # Generic fallback
            if "package.json" in paths:
                commands.append("npm test")
            elif any(p.endswith(".py") for p in paths):
                commands.append("python -m pytest")

        return commands

    def _describe_structure(
        self, file_tree: List[Dict[str, Any]]
    ) -> list[str]:
        """Create a simplified directory structure description.

        Args:
            file_tree: Repository file tree.

        Returns:
            List of formatted structure lines.
        """
        # Get top-level items
        top_items: dict[str, str] = {}  # name -> type
        for entry in file_tree:
            path = entry["path"]
            if "/" not in path:
                item_type = "dir" if entry.get("type") == "tree" else "file"
                top_items[path] = item_type
            else:
                top_dir = path.split("/")[0]
                top_items[top_dir] = "dir"

        lines = ["."]

        sorted_items = sorted(top_items.items(), key=lambda x: (x[1] != "dir", x[0]))

        for i, (name, item_type) in enumerate(sorted_items[:15]):
            is_last = i == len(sorted_items[:15]) - 1
            prefix = "└── " if is_last else "├── "
            suffix = "/" if item_type == "dir" else ""
            description = ""

            # Add descriptions for known directories
            from app.services.diagram_generator import DiagramGenerator
            desc = DiagramGenerator.FRAMEWORK_DIRS.get(name.lower(), "")
            if desc:
                description = f"  # {desc}"

            lines.append(f"{prefix}{name}{suffix}{description}")

        if len(top_items) > 15:
            lines.append(f"└── ... ({len(top_items) - 15} more items)")

        return lines
