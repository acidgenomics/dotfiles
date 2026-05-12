# Development Workflow

## Git

- Do not commit or push — leave all version control to the user.

## Tooling

- Assume all CLI tools are available on PATH; never use `.venv` paths to invoke
  them.
- Never install packages or add dependencies without being explicitly asked.
- Never override or ignore configuration in `pyproject.toml`.

## Linting & Type Checking

- Never suppress linting errors with `# noqa`, `eslint-disable`, or similar —
  fix the underlying code.
- Never silently skip linting or type-checking steps.
