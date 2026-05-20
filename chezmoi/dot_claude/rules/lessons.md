# Lessons

> Cross-project patterns. Managed in chezmoi — edit the source, not ~/.claude directly.
> Per-project lessons go in .claude/rules/lessons.md within the repo.

## JSON Formatting

- Always use 2-space indentation for JSON files. Never use 4 spaces.
- This applies to all JSON: config files, `.claude/settings.json`, package.json,
  tsconfig, etc.
- When writing or reformatting JSON, use `json.dumps(obj, indent=2)` or
  `JSON.stringify(obj, null, 2)`.
