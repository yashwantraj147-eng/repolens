"""Shared test fixtures and configuration."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a FastAPI test client.

    Returns:
        TestClient instance for making requests.
    """
    return TestClient(app)


@pytest.fixture
def sample_repo_data() -> dict:
    """Sample GitHub API response for a repository.

    Returns:
        Dictionary mimicking the GitHub repos API response.
    """
    return {
        "name": "fastapi",
        "full_name": "fastapi/fastapi",
        "html_url": "https://github.com/fastapi/fastapi",
        "description": "FastAPI framework, high performance, easy to learn",
        "language": "Python",
        "stargazers_count": 75000,
        "forks_count": 6000,
        "open_issues_count": 500,
        "created_at": "2018-12-08T00:00:00Z",
        "updated_at": "2024-06-01T00:00:00Z",
        "default_branch": "main",
        "topics": ["python", "api", "fastapi"],
        "has_wiki": True,
        "license": {"spdx_id": "MIT"},
        "size": 50000,
        "owner": {"login": "fastapi"},
    }


@pytest.fixture
def sample_tree_data() -> dict:
    """Sample GitHub API response for a file tree.

    Returns:
        Dictionary mimicking the GitHub trees API response.
    """
    return {
        "sha": "abc123",
        "tree": [
            {"path": "README.md", "type": "blob", "size": 5000},
            {"path": "LICENSE", "type": "blob", "size": 1100},
            {"path": "setup.py", "type": "blob", "size": 800},
            {"path": "requirements.txt", "type": "blob", "size": 200},
            {"path": ".github", "type": "tree"},
            {"path": ".github/workflows", "type": "tree"},
            {"path": ".github/workflows/ci.yml", "type": "blob", "size": 500},
            {"path": "src", "type": "tree"},
            {"path": "src/__init__.py", "type": "blob", "size": 0},
            {"path": "src/main.py", "type": "blob", "size": 3000},
            {"path": "src/utils.py", "type": "blob", "size": 1500},
            {"path": "tests", "type": "tree"},
            {"path": "tests/__init__.py", "type": "blob", "size": 0},
            {"path": "tests/test_main.py", "type": "blob", "size": 2000},
            {"path": "docs", "type": "tree"},
            {"path": "docs/index.md", "type": "blob", "size": 1000},
            {"path": "CONTRIBUTING.md", "type": "blob", "size": 2000},
            {"path": "CODE_OF_CONDUCT.md", "type": "blob", "size": 3000},
        ],
        "truncated": False,
    }


@pytest.fixture
def sample_readme() -> str:
    """Sample README content.

    Returns:
        A realistic README string.
    """
    return """# FastAPI

[![CI](https://img.shields.io/badge/ci-passing-green)]()
[![Coverage](https://img.shields.io/badge/coverage-95%25-green)]()

FastAPI framework, high performance, easy to learn, fast to code, ready for production.

## Installation

```bash
pip install fastapi
```

## Quick Start

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

## Features

- Fast: Very high performance, on par with NodeJS and Go.
- Fast to code: Increase the speed to develop features by about 200% to 300%.
- Fewer bugs: Reduce about 40% of human (developer) induced errors.

## Documentation

Full documentation is at https://fastapi.tiangolo.com

![FastAPI](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)
"""
