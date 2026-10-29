"""Repository summary generator.

Produces a plain-English summary of what a repository does,
using either an LLM or template-based heuristics.
"""

from typing import Any, Dict, List, Optional

from app.config import Settings
from app.models.schemas import RepoInfo
from app.services.llm.base import LLMProvider
from app.services.llm.local import LocalProvider
from app.services.llm.openai import OpenAIProvider


class SummaryGenerator:
    """Generates plain-English summaries of GitHub repositories.

    Uses an LLM provider if available, otherwise falls back to
    intelligent template-based generation using repo metadata.
    """

    def __init__(self, settings: Settings) -> None:
        """Initialize the summary generator.

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
        languages: Optional[Dict[str, int]] = None,
        file_tree: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Generate a plain-English summary of the repository.

        Args:
            repo_info: Repository metadata.
            readme_content: Raw README content.
            languages: Language breakdown.
            file_tree: Repository file tree.

        Returns:
            A human-readable summary string.
        """
        # Try LLM-based generation if available (and it's not the local provider)
        if isinstance(self.llm, OpenAIProvider) and await self.llm.is_available():
            try:
                return await self._generate_with_llm(
                    repo_info, readme_content, languages, file_tree
                )
            except Exception:
                pass  # Fall back to template

        # Template-based generation
        return self._generate_from_template(
            repo_info, readme_content, languages, file_tree
        )

    async def _generate_with_llm(
        self,
        repo_info: RepoInfo,
        readme_content: Optional[str],
        languages: Optional[Dict[str, int]],
        file_tree: Optional[List[Dict[str, Any]]],
    ) -> str:
        """Generate summary using an LLM provider.

        Args:
            repo_info: Repository metadata.
            readme_content: Raw README content.
            languages: Language breakdown.
            file_tree: Repository file tree.

        Returns:
            LLM-generated summary string.
        """
        # Build context for the LLM
        context_parts = [
            f"Repository: {repo_info.owner}/{repo_info.name}",
            f"Description: {repo_info.description or 'No description'}",
            f"Primary Language: {repo_info.language or 'Unknown'}",
            f"Stars: {repo_info.stars}, Forks: {repo_info.forks}",
            f"Topics: {', '.join(repo_info.topics) if repo_info.topics else 'None'}",
        ]

        if languages:
            top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            context_parts.append(f"Languages: {', '.join(l[0] for l in top_langs)}")

        if readme_content:
            # Truncate README to avoid token limits
            readme_excerpt = readme_content[:2000]
            context_parts.append(f"README excerpt:\n{readme_excerpt}")

        context = "\n".join(context_parts)

        prompt = (
            "You are an expert software analyst. Given the following information about a "
            "GitHub repository, write a concise 2-3 paragraph summary that explains:\n"
            "1. What the project does and its main purpose\n"
            "2. Key technologies and architecture approach\n"
            "3. Who would use it and why it matters\n\n"
            f"{context}\n\n"
            "Write a clear, professional summary:"
        )

        return await self.llm.generate(prompt, max_tokens=500)

    def _generate_from_template(
        self,
        repo_info: RepoInfo,
        readme_content: Optional[str],
        languages: Optional[Dict[str, int]],
        file_tree: Optional[List[Dict[str, Any]]],
    ) -> str:
        """Generate summary using template-based heuristics.

        Args:
            repo_info: Repository metadata.
            readme_content: Raw README content.
            languages: Language breakdown.
            file_tree: Repository file tree.

        Returns:
            Template-generated summary string.
        """
        parts: list[str] = []

        # Opening line
        name = repo_info.name
        desc = repo_info.description
        if desc:
            parts.append(f"**{repo_info.owner}/{name}** is {desc.rstrip('.')}.")
        else:
            parts.append(f"**{repo_info.owner}/{name}** is a {repo_info.language or 'software'} project hosted on GitHub.")

        # Language and tech info
        if languages and len(languages) > 1:
            total = sum(languages.values())
            top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:4]
            lang_parts = []
            for lang, byte_count in top_langs:
                pct = round(byte_count / total * 100) if total > 0 else 0
                lang_parts.append(f"{lang} ({pct}%)")
            parts.append(
                f"The codebase is primarily written in {', '.join(lang_parts)}."
            )
        elif repo_info.language:
            parts.append(f"The project is written in {repo_info.language}.")

        # Project structure insights
        if file_tree:
            dir_names = {
                entry["path"].split("/")[0].lower()
                for entry in file_tree
                if "/" in entry["path"]
            }
            structure_hints = []
            if "src" in dir_names or "app" in dir_names or "lib" in dir_names:
                structure_hints.append("a well-organized source structure")
            if "tests" in dir_names or "test" in dir_names or "__tests__" in dir_names:
                structure_hints.append("a test suite")
            if "docs" in dir_names:
                structure_hints.append("dedicated documentation")
            if any("docker" in d for d in dir_names) or any(
                "dockerfile" in entry["path"].lower() for entry in file_tree
            ):
                structure_hints.append("Docker containerization")
            if any(".github" in d for d in dir_names):
                structure_hints.append("GitHub Actions CI/CD")

            if structure_hints:
                parts.append(
                    f"The repository features {self._join_list(structure_hints)}."
                )

        # Popularity
        if repo_info.stars >= 1000:
            parts.append(
                f"With {repo_info.stars:,} stars and {repo_info.forks:,} forks, "
                f"it is a well-established project in the open-source community."
            )
        elif repo_info.stars >= 100:
            parts.append(
                f"The project has gained traction with {repo_info.stars:,} stars "
                f"and {repo_info.forks:,} forks on GitHub."
            )
        elif repo_info.stars > 0:
            parts.append(
                f"The project has {repo_info.stars} star(s) and {repo_info.forks} fork(s) on GitHub."
            )

        # Topics
        if repo_info.topics:
            parts.append(f"Key topics: {', '.join(repo_info.topics[:8])}.")

        return " ".join(parts)

    @staticmethod
    def _join_list(items: list[str]) -> str:
        """Join a list of items into a grammatically correct string.

        Args:
            items: List of string items.

        Returns:
            Comma-separated string with 'and' before the last item.
        """
        if len(items) == 0:
            return ""
        elif len(items) == 1:
            return items[0]
        elif len(items) == 2:
            return f"{items[0]} and {items[1]}"
        else:
            return f"{', '.join(items[:-1])}, and {items[-1]}"
