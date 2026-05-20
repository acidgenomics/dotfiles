# Workflow Orchestration

> These rules apply when working in a project directory (git repo, structured
> codebase). For ad-hoc tasks or general questions, follow the behavior rules in
> CLAUDE.md.

## Behavior in Plan Mode

Plan mode is a conversation, not a race to produce a plan document.

- Start by understanding the problem. Ask questions, challenge assumptions,
  suggest alternatives.
- Keep responses short — whiteboard talk, not essays.
- Don't write a formal plan or call ExitPlanMode until I explicitly say I'm
  ready.
- "Write the plan," "looks good, let's do it," or similar = green light to
  formalize. Nothing else is.

## 1. Plan Mode Default

- Enter plan mode for tasks involving architectural decisions or changes with
  non-obvious tradeoffs.
- If something goes sideways, STOP and re-plan immediately — don't keep pushing.
- Use plan mode for verification steps, not just building.
- Write detailed specs upfront to reduce ambiguity.

## 2. Subagent Strategy

- Use subagents liberally to keep main context window clean.
- Offload research, exploration, and parallel analysis to subagents.
- For complex problems, throw more compute at it via subagents.
- One task per subagent for focused execution.

## 3. Self-Improvement Loop

- After ANY correction from the user: update `.claude/rules/lessons.md` with the
  pattern (project-level only — skip if no `.claude/rules/` directory exists).
- Write rules for yourself that prevent the same mistake.
- Ruthlessly iterate on these lessons until mistake rate drops.
- Global cross-project patterns live in `~/.claude/rules/lessons.md` (auto-loaded,
  user-curated in chezmoi). Per-project lessons live in `.claude/rules/lessons.md`
  within the repo (Claude-maintained). Both are auto-loaded into context.

## 4. Verification Before Done

- Never mark a task complete without proving it works.
- Diff behavior between main and your changes when relevant.
- Ask yourself: "Would a staff engineer approve this?".
- Run tests, check logs, demonstrate correctness.

## 5. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding.
- Point at logs, errors, failing tests — then resolve them.
- Zero context switching required from the user.
- Go fix failing CI tests without being told how.

## Plan Files

- Save plan files to `.claude/plans/` within the current project directory.
- Name with a date prefix: `YYYY-MM-DD-plan-name.md` (e.g.
  `2026-05-19-m2a-assay-migration.md`).

## Task Management

1. **Plan First**: Write plan to `.claude/todo.md` with checkable items.
2. **Verify Plan**: Check in before starting implementation.
3. **Track Progress**: Mark items complete as you go.
4. **Explain Changes**: High-level summary at each step.
5. **Document Results**: Add review section to `.claude/todo.md`.
6. **Capture Lessons**: Update `.claude/rules/lessons.md` after corrections.

## Session Hygiene

Context is the constraint. Long sessions with accumulated failed attempts
perform worse than fresh sessions with a better prompt.

- After two failed corrections on the same issue, STOP. Summarize what you
  learned and ask the user to reset the session with a sharper prompt.
- Do not keep pushing the same approach after it has failed twice — this
  compounds context pollution and degrades output quality.
- Use subagents for exploration tasks that would pollute the main context with
  many file reads.

## Git Hygiene

- Write descriptive commit messages: subject under 72 chars, body explains the
  why not just the what.
- Never write "update file", "fix bug", "WIP", or "changes" as a commit message.

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Minimal code
  impact.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer
  standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid
  introducing bugs.
