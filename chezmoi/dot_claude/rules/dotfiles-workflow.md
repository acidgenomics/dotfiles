# Workflow Orchestration

Use subagents liberally to keep the main context clean. One task per agent.
After any correction, update the project's lessons rule:
`.claude/rules/<prefix>-lessons.md` if the repo prefixes its rules, else
`.claude/rules/lessons.md` (project-level only; `~/.claude/rules/dotfiles-lessons.md`
is user-curated).

> For plan mode etiquette, operating principles, session hygiene, and git commit
> conventions, invoke the `dotfiles-workflow-guidance` skill.
