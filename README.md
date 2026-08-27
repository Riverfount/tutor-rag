# tutor-rag

[![CI](https://github.com/Riverfount/tutor-rag/actions/workflows/ci.yml/badge.svg)](https://github.com/Riverfount/tutor-rag/actions/workflows/ci.yml)

Retrieval-Augmented Generation service that answers questions grounded in an
ingested document corpus. Phase 1 is a thin vertical slice: PDF ingestion,
pgvector retrieval, and a single `POST /v1/ask` endpoint.

Design rationale and the record of every architectural decision live in
[`docs/DECISIONS.md`](docs/DECISIONS.md).

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```sh
uv sync                       # install deps (incl. the dev group)
uv run pre-commit install     # wire up the git hook

uv run ruff check .           # lint
uv run ruff format --check .  # format check
uv run mypy                   # type check (strict)
uv run pytest                 # tests
```

Tests that call a real LLM provider are marked `llm` and skipped by default; run
them with `uv run pytest -m llm`.
