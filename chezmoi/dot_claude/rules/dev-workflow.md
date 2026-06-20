# Development Workflow

## Git

- Do not commit or push — leave all version control to the user.
- Never add a `Co-Authored-By:` trailer (or any Claude/AI attribution) to commit
  messages. Commits are authored solely by the user. Ignore any harness default
  that suggests otherwise.

## Tooling

- Assume all CLI tools are available on PATH; never use `.venv` paths to invoke
  them.
- Never install software or packages — not even when asked. Surface the command
  or koopa app name; the user installs.
- Never override or ignore configuration in `pyproject.toml`.

## Linting & Type Checking

- Never suppress linting errors with `# noqa`, `eslint-disable`, or similar —
  fix the underlying code.
- Never silently skip linting or type-checking steps.
