# Lessons

> Cross-project patterns. Managed in chezmoi — edit the source, not ~/.claude directly.
> Per-project lessons go in .claude/rules/lessons.md within the repo.

## Plan Files: System-Generated Names Must Be Used As-Is

When the system specifies a plan filename (in the plan mode system message), use that exact path — do NOT rename it with a `YYYY-MM-DD-` prefix. VS Code's plan review UI looks for the exact filename the system specified; renaming breaks the UI.

The `YYYY-MM-DD-` date prefix convention applies only to manually created plan/reference docs, not system-assigned plan filenames.

## JSON Formatting

- Always use 2-space indentation for JSON files. Never use 4 spaces.
- This applies to all JSON: config files, `.claude/settings.json`, package.json,
  tsconfig, etc.
- When writing or reformatting JSON, use `json.dumps(obj, indent=2)` or
  `JSON.stringify(obj, null, 2)`.
