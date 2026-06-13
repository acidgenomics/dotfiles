# Workflow Orchestration

> Applies when working in a project directory. For ad-hoc tasks, see CLAUDE.md.

## Plan Mode

A conversation, not a race. Start by understanding the problem — ask questions,
challenge assumptions. Don't call ExitPlanMode until explicitly given the green
light. Enter plan mode for architectural decisions or non-obvious tradeoffs.

## Operating Principles

- **Subagents**: use liberally to keep the main context clean. One task per agent.
- **Self-improvement**: after any correction, update `.claude/rules/lessons.md`
  (project-level only; `~/.claude/rules/lessons.md` is user-curated).
- **Verification**: never mark done without proof. Run tests, check logs.
- **Bug fixing**: given a bug report, just fix it.
- **Elegance**: for non-trivial changes, ask "is there a more elegant way?"
- **Session hygiene**: after two failed corrections, STOP and reset with a sharper prompt.

## Plan Files & Task Management

Save to `.claude/plans/`. Use system-assigned filenames as-is.
Plan → verify → track → explain → capture lessons.

## Git Hygiene

Subject ≤72 chars; body explains why. Never "update", "fix bug", "WIP", "changes".
