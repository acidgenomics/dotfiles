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

## Deep Research Should Always Include GitHub Code Search

When running deep-research workflows on technical/protocol questions, always include a second parallel workflow specifically targeting GitHub code and repository implementations. The canonical workflow is two parallel runs:
1. Web/protocol research (standards docs, blog posts, issue trackers)
2. GitHub code search (real implementations, usage patterns, adoption evidence)

GitHub code search routinely surfaces implementation details (exact escape sequences, version numbers, adoption tables) that are absent from web sources. This pattern found the definitive mode 2031 solution that was missed by web search alone.
