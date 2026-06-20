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

## Never Install Software

Enforced by `guard-installs.sh` hook. Surface the command and stop.

## Never Add Co-Authored-By Trailers

Never add `Co-Authored-By:` lines to commit messages in any repo. The user
does not want Claude attribution in git history or GitHub commit views.
