# Workflow Orchestration

Use subagents liberally to keep the main context clean. One task per agent.
After any correction, update the project's lessons rule:
`.agents/rules/<prefix>-lessons.md` if the repo prefixes its rules, else
`.agents/rules/lessons.md` (project-level only; `~/.agents/rules/dotfiles-lessons.md`
is user-curated). When the project routes skill-specific lessons to the owning skill's
Gotchas, follow the project's rule instead.

> For plan mode etiquette, operating principles, session hygiene, and git commit
> conventions, invoke the `koopa-workflow-guidance` skill.
