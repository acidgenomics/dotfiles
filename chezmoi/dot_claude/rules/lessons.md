# Lessons

> Cross-project patterns. Edit the chezmoi source, not ~/.claude directly.
> Per-project lessons: .claude/rules/lessons.md within the repo.

## Plan Files: Use System-Generated Names As-Is

Never rename with a `YYYY-MM-DD-` prefix — the VS Code plan UI requires the exact
filename. Date prefixes apply only to manually created docs.

## JSON Formatting

Always 2-space indentation. Never 4 spaces.

## Deep Research: Always Include GitHub Code Search

Run a second parallel workflow targeting GitHub code search alongside web
research. GitHub surfaces implementation details absent from web sources.

## Never Use `/tmp` for Sensitive Files

Use `mktemp` (respects `$TMPDIR`). In Python: `tempfile.mkstemp()`. Delete immediately.

> Git-history surgery: use the `git-history-surgery` skill.

## Path-Scoped Rule Globs Must Account for chezmoi Filename Prefixes

A `paths:`-scoped rule in `~/.claude/rules/` matching `**/*.sh` silently covers
**zero** chezmoi shell sources: they are named `dot_zprofile-work.tmpl`,
`dot_bashrc-work`, `install` — no `.sh` suffix. `shell.md` carried the correct
4-space rule for months while every file it mattered for went unmatched. A
rule that never fires looks identical to a rule that does not exist. When
adding a path-scoped rule, test the globs against actual `git ls-files` output
before trusting it, and mirror the convention into `.editorconfig`
(declarative, editor-visible) rather than relying on prose alone.

Two nuances: an `.editorconfig` section glob matches on **basename** for a
bare pattern, so extension-less files need explicit brace lists
(`{install,dot_profile*,...}`); and a child `.editorconfig` must **omit**
`root=true` to override one property while inheriting the rest from a parent.

## SKILL.md Descriptions Must Be Compatible with Both Claude Code and Copilot CLI

Always use `description: >-` (folded-strip block scalar). Never inline (`description: ...`
on one line) and never plain `>` (folded adds a trailing `\n`, pushing parsed length to
`raw + 1`). Rules:

- Keep raw description text ≤1023 chars. Copilot CLI enforces a 1024-char limit on the
  parsed value; `>-` makes parsed == raw, so 1023 raw == 1023 parsed — safely under.
- Never put `key: value` patterns (colon-space) inside the description text. Copilot's
  YAML parser treats them as mapping entries and rejects the file. Block scalar sidesteps
  the ambiguity entirely.
- A single skill over the limit causes Copilot to reject the **entire** `.claude/skills/`
  directory load ("Failed to load N skills") — it is not a per-skill failure.
