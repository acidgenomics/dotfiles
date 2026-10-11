# Lessons

> Cross-project patterns. Edit the chezmoi source, not ~/.agents or ~/.claude directly.
> Per-project lessons: the repo's `.agents/rules/<prefix>-lessons.md` (or
> `lessons.md` if the repo does not prefix its rules).

- **Plan files: keep the system-generated name as-is.** The VS Code plan UI needs the exact filename. Date prefixes apply only to manually created docs.
- **Session reports go to `~/Documents/bucket/YYYY/MM/DD/<slug>.md` (Obsidian vault),** not a repo `reports/` or `.claude/reports/` (gitignored, so invisible to git). No date prefix in the filename. Add YAML frontmatter with `type: report`, `title`, `date`. Never save a report to `.claude/plans/`.
- **JSON uses 2-space indentation, never 4.**
- **Deep research: run a second parallel workflow on GitHub code search** alongside web research. It surfaces implementation details absent from web sources.
- **Never use `/tmp` for sensitive files.** Use `mktemp` (respects `$TMPDIR`); in Python `tempfile.mkstemp()`. Delete immediately.
- **Never reach for a tool outside the current project without asking.** Don't invoke a binary from another project's venv/node_modules or trigger any download (even a small one) to unblock verification. Surface the missing capability and the command that would add it, and let the user decide. The violation is installing without asking, not the size or location.
- **Path-scoped rule globs must account for chezmoi filename prefixes** (`dot_`, `.tmpl`, extension-less `install`). Test globs against `git ls-files` and mirror the convention into `.editorconfig`. → `dotfiles-maintain-claude-config` skill.
- **SKILL.md `description:` uses `>-` and stays at most 1023 chars.** → `dotfiles-maintain-claude-config` skill.
- **Git-history surgery:** use the `dotfiles-git-history-surgery` skill.
