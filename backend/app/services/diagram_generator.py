"""Architecture diagram generator using Mermaid syntax.

Inspects repository file structure and generates a visual architecture
diagram in Mermaid markup format.
"""

import re
from typing import Any, Dict, List, Optional, Set

from app.models.schemas import RepoInfo


class DiagramGenerator:
    """Generates Mermaid architecture diagrams from repository structure.

    Analyzes the file tree to detect project type, key modules,
    and relationships, then emits a Mermaid graph.
    """

    # Common entry points by language/framework
    ENTRY_POINTS = {
        "main.py", "app.py", "server.py", "index.py", "wsgi.py", "asgi.py",
        "manage.py", "run.py",
        "index.js", "index.ts", "server.js", "server.ts", "app.js", "app.ts",
        "main.js", "main.ts", "main.jsx", "main.tsx",
        "App.jsx", "App.tsx", "App.js", "App.vue",
        "main.go", "cmd/main.go",
        "Main.java", "Application.java",
        "main.rs", "lib.rs",
        "Program.cs", "Startup.cs",
    }

    # Config files that indicate project structure
    CONFIG_FILES = {
        "package.json": "Node.js",
        "requirements.txt": "Python",
        "Pipfile": "Python",
        "pyproject.toml": "Python",
        "setup.py": "Python",
        "go.mod": "Go",
        "Cargo.toml": "Rust",
        "pom.xml": "Java/Maven",
        "build.gradle": "Java/Gradle",
        "Gemfile": "Ruby",
        "composer.json": "PHP",
    }

    # Framework-specific directories
    FRAMEWORK_DIRS = {
        "src": "source",
        "lib": "library",
        "app": "application",
        "api": "API",
        "routes": "routing",
        "routers": "routing",
        "controllers": "controllers",
        "services": "services",
        "models": "models",
        "views": "views",
        "templates": "templates",
        "components": "components",
        "pages": "pages",
        "hooks": "hooks",
        "utils": "utilities",
        "helpers": "helpers",
        "middleware": "middleware",
        "static": "static assets",
        "public": "public assets",
        "assets": "assets",
        "config": "configuration",
        "db": "database",
        "database": "database",
        "migrations": "migrations",
        "tests": "testing",
        "test": "testing",
        "docs": "documentation",
        "scripts": "scripts",
        "deploy": "deployment",
        "infra": "infrastructure",
        "terraform": "infrastructure",
        "k8s": "kubernetes",
        "docker": "containerization",
    }

    def generate(
        self,
        repo_info: RepoInfo,
        file_tree: List[Dict[str, Any]],
        languages: Optional[Dict[str, int]] = None,
    ) -> str:
        """Generate a Mermaid architecture diagram for the repository.

        Args:
            repo_info: Repository metadata.
            file_tree: List of file tree entries with 'path' and 'type'.
            languages: Optional language breakdown (language -> bytes).

        Returns:
            Mermaid diagram markup string.
        """
        languages = languages or {}

        # Detect project type
        project_type = self._detect_project_type(file_tree, languages)

        # Get top-level directories
        top_dirs = self._get_top_level_dirs(file_tree)

        # Get key files
        key_files = self._get_key_files(file_tree)

        # Detect infrastructure
        infra = self._detect_infrastructure(file_tree)

        # Build the diagram
        return self._build_diagram(
            repo_info, project_type, top_dirs, key_files, infra, languages
        )

    def _detect_project_type(
        self,
        file_tree: List[Dict[str, Any]],
        languages: Dict[str, int],
    ) -> str:
        """Detect the project type from file structure and languages.

        Args:
            file_tree: Repository file tree.
            languages: Language breakdown.

        Returns:
            Project type string (e.g., 'fullstack', 'backend', 'frontend').
        """
        paths = {entry["path"].lower() for entry in file_tree}
        path_list = list(paths)

        has_frontend = any(
            p in paths
            for p in ["package.json", "index.html", "vite.config.js", "next.config.js",
                       "angular.json", "vue.config.js", "webpack.config.js"]
        ) or any(p.startswith("src/") and p.endswith((".jsx", ".tsx", ".vue")) for p in path_list)

        has_backend = any(
            p in paths
            for p in ["requirements.txt", "go.mod", "cargo.toml", "pom.xml",
                       "gemfile", "setup.py", "pyproject.toml", "manage.py"]
        )

        has_api = any(
            any(seg in p for seg in ["api/", "routes/", "routers/", "controllers/", "endpoints/"])
            for p in path_list
        )

        # Check for monorepo
        has_packages = any(
            p.startswith("packages/") or p.startswith("apps/") or p.startswith("services/")
            for p in path_list
        )

        if has_packages:
            return "monorepo"
        elif has_frontend and (has_backend or has_api):
            return "fullstack"
        elif has_frontend:
            return "frontend"
        elif has_backend or has_api:
            return "backend"
        elif languages:
            # Library/tool
            return "library"
        else:
            return "project"

    def _get_top_level_dirs(
        self, file_tree: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract meaningful top-level directories.

        Args:
            file_tree: Repository file tree.

        Returns:
            List of top-level directory names (excluding hidden dirs).
        """
        dirs: Set[str] = set()
        for entry in file_tree:
            path = entry["path"]
            if "/" in path:
                top = path.split("/")[0]
                if not top.startswith(".") and entry.get("type") != "blob":
                    dirs.add(top)
            elif entry.get("type") == "tree":
                if not path.startswith("."):
                    dirs.add(path)

        # Also add dirs inferred from blob paths
        for entry in file_tree:
            if "/" in entry["path"]:
                top = entry["path"].split("/")[0]
                if not top.startswith("."):
                    dirs.add(top)

        return sorted(dirs)

    def _get_key_files(
        self, file_tree: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify key files (entry points, configs) in the repository.

        Args:
            file_tree: Repository file tree.

        Returns:
            List of key file paths.
        """
        key_files = []
        for entry in file_tree:
            if entry.get("type") != "blob":
                continue
            filename = entry["path"].split("/")[-1]
            if filename in self.ENTRY_POINTS or filename in self.CONFIG_FILES:
                key_files.append(entry["path"])
        return key_files

    def _detect_infrastructure(
        self, file_tree: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Detect infrastructure and tooling setup.

        Args:
            file_tree: Repository file tree.

        Returns:
            Dict of infrastructure flags.
        """
        paths = {entry["path"].lower() for entry in file_tree}
        path_list = list(paths)

        return {
            "docker": any("dockerfile" in p or "docker-compose" in p for p in path_list),
            "ci": any(
                p.startswith(".github/workflows/") or p in (".travis.yml", ".gitlab-ci.yml")
                for p in path_list
            ),
            "database": any(
                any(db in p for db in ["migrations/", "schema", "prisma/", "alembic/", "sequelize"])
                for p in path_list
            ),
            "docs": any(p.startswith("docs/") or p.startswith("doc/") for p in path_list),
            "tests": any(
                p.startswith("tests/") or p.startswith("test/") or p.startswith("__tests__/")
                for p in path_list
            ),
        }

    def _build_diagram(
        self,
        repo_info: RepoInfo,
        project_type: str,
        top_dirs: List[str],
        key_files: List[str],
        infra: Dict[str, bool],
        languages: Dict[str, int],
    ) -> str:
        """Build the Mermaid diagram markup.

        Args:
            repo_info: Repository metadata.
            project_type: Detected project type.
            top_dirs: Top-level directories.
            key_files: Key file paths.
            infra: Infrastructure flags.
            languages: Language breakdown.

        Returns:
            Mermaid graph markup string.
        """
        lines = ["graph TD"]

        # Root node
        lang_str = repo_info.language or "Multi-language"
        lines.append(f'    ROOT["{repo_info.name}<br/>{lang_str} {project_type}"]')
        lines.append(f'    style ROOT fill:#4f46e5,stroke:#3730a3,color:#fff')

        # Group directories by category
        source_dirs = []
        infra_dirs = []
        support_dirs = []

        for d in top_dirs:
            lower_d = d.lower()
            category = self.FRAMEWORK_DIRS.get(lower_d, "")
            if category in ("source", "application", "API", "routing", "controllers",
                          "services", "models", "views", "components", "pages",
                          "hooks", "library", "middleware"):
                source_dirs.append(d)
            elif category in ("testing", "documentation", "deployment",
                             "infrastructure", "kubernetes", "containerization",
                             "scripts"):
                infra_dirs.append(d)
            elif category in ("static assets", "public assets", "assets",
                             "configuration", "database", "migrations",
                             "templates", "utilities", "helpers"):
                support_dirs.append(d)
            else:
                source_dirs.append(d)

        # Source code subgraph
        if source_dirs:
            lines.append('    subgraph SRC["Source Code"]')
            for d in source_dirs[:8]:  # Limit to prevent giant diagrams
                node_id = self._sanitize_id(d)
                label = self.FRAMEWORK_DIRS.get(d.lower(), d)
                label = label.title() if label != d else d
                lines.append(f'        {node_id}["{d}/"]')
            lines.append('    end')
            lines.append('    ROOT --> SRC')
            lines.append('    style SRC fill:#1e1b4b,stroke:#4f46e5,color:#c7d2fe')

        # Support subgraph
        if support_dirs:
            lines.append('    subgraph SUPPORT["Support & Config"]')
            for d in support_dirs[:6]:
                node_id = self._sanitize_id(d)
                label = self.FRAMEWORK_DIRS.get(d.lower(), d)
                lines.append(f'        {node_id}["{d}/"]')
            lines.append('    end')
            lines.append('    ROOT --> SUPPORT')
            lines.append('    style SUPPORT fill:#1e1b4b,stroke:#6366f1,color:#c7d2fe')

        # Infrastructure subgraph
        infra_items = []
        if infra.get("docker"):
            infra_items.append(("DOCKER", "Docker", "fa:fa-docker"))
        if infra.get("ci"):
            infra_items.append(("CI", "CI/CD", "fa:fa-cogs"))
        if infra.get("database"):
            infra_items.append(("DB", "Database", "fa:fa-database"))
        if infra_dirs:
            for d in infra_dirs[:4]:
                node_id = self._sanitize_id(d)
                infra_items.append((node_id, d, ""))

        if infra_items:
            lines.append('    subgraph INFRA["Infrastructure"]')
            for node_id, label, _icon in infra_items:
                lines.append(f'        {node_id}["{label}"]')
            lines.append('    end')
            lines.append('    ROOT --> INFRA')
            lines.append('    style INFRA fill:#1e1b4b,stroke:#818cf8,color:#c7d2fe')

        # Add relationships between source dirs if applicable
        if len(source_dirs) >= 2:
            # Common relationship patterns
            dir_set = {d.lower() for d in source_dirs}
            relationships = [
                ("routers", "services", "calls"),
                ("routes", "controllers", "routes to"),
                ("controllers", "services", "uses"),
                ("controllers", "models", "uses"),
                ("services", "models", "uses"),
                ("pages", "components", "renders"),
                ("views", "models", "reads"),
                ("api", "services", "calls"),
                ("app", "models", "uses"),
                ("src", "lib", "imports"),
            ]
            for src, dst, label in relationships:
                if src in dir_set and dst in dir_set:
                    src_id = self._sanitize_id(src)
                    dst_id = self._sanitize_id(dst)
                    # Find original case
                    for d in source_dirs:
                        if d.lower() == src:
                            src_id = self._sanitize_id(d)
                        if d.lower() == dst:
                            dst_id = self._sanitize_id(d)
                    lines.append(f'    {src_id} -->|"{label}"| {dst_id}')

        # Languages section (if multiple)
        if len(languages) > 1:
            top_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
            total = sum(languages.values())
            lang_parts = []
            for lang, bytes_count in top_langs:
                pct = (bytes_count / total * 100) if total > 0 else 0
                lang_parts.append(f"{lang} {pct:.0f}%")
            lang_label = " | ".join(lang_parts)
            lines.append(f'    LANGS["{lang_label}"]')
            lines.append(f'    style LANGS fill:#0f172a,stroke:#475569,color:#94a3b8')
            lines.append(f'    ROOT -.- LANGS')

        return "\n".join(lines)

    @staticmethod
    def _sanitize_id(name: str) -> str:
        """Convert a directory name to a valid Mermaid node ID.

        Args:
            name: Directory or file name.

        Returns:
            Sanitized identifier string.
        """
        # Remove special characters, replace with underscores
        sanitized = re.sub(r"[^a-zA-Z0-9]", "_", name)
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "d_" + sanitized
        return sanitized.upper()
