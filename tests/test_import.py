"""Smoke test: the editable install resolves and the package tree imports."""

import importlib


def test_package_tree_imports() -> None:
    pkg = importlib.import_module("tutor_rag")
    assert callable(pkg.main)

    for name in ("core", "infra", "api", "ingestion"):
        importlib.import_module(f"tutor_rag.{name}")
