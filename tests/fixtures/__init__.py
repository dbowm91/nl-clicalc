"""Fixture loader for golden test corpus."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

FIXTURES_DIR = Path(__file__).parent


def load_fixture(relative_path: str) -> dict[str, Any]:
    """Load a JSON fixture file by relative path from the fixtures directory."""
    full_path = FIXTURES_DIR / relative_path
    if not full_path.exists():
        raise FileNotFoundError(f"Fixture not found: {full_path}")
    with open(full_path, encoding="utf-8") as f:
        return json.load(f)


def list_fixtures(subdir: str | None = None) -> list[str]:
    """List all .json fixture files, optionally filtered by subdirectory."""
    search_dir = FIXTURES_DIR / subdir if subdir else FIXTURES_DIR
    fixtures = []
    for root, _dirs, files in os.walk(search_dir):
        for fname in sorted(files):
            if fname.endswith(".json") and fname != "mcp_tool_registry_expected.json":
                rel = os.path.relpath(os.path.join(root, fname), FIXTURES_DIR)
                fixtures.append(rel)
    return fixtures


def load_all_fixtures(subdir: str | None = None) -> list[tuple[str, dict[str, Any]]]:
    """Load all fixtures as (relative_path, fixture_data) pairs."""
    results = []
    for rel in list_fixtures(subdir):
        results.append((rel, load_fixture(rel)))
    return results
