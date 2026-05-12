# Python Style

## Code Style

- Follow PEP 8, enforced via `ruff`. Match line length and quote style from
  `pyproject.toml`.
- Always check existing patterns before introducing new ones.

## Type Annotations

- Use native type hints for the target Python version.
- Do NOT use `from __future__ import annotations`.
- Use `X | Y` union syntax (Python 3.10+); prefer `X | None` over `Optional[X]`.
- Annotate all function signatures (parameters and return types).
- Use `typing.TypeAlias` for complex type aliases.
