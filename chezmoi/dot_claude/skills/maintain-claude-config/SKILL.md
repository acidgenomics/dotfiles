---
name: maintain-claude-config
description: >
  Guide for maintaining and optimizing Claude Code configuration — CLAUDE.md,
  rules files, hooks, and skills. Use when auditing instruction bloat, deciding
  where a new rule belongs, or pruning stale content.
---

# Maintaining Claude Code Configuration

## Core Principle: Progressive Disclosure

Configuration that loads unconditionally on every session costs tokens every
time, whether relevant or not. The goal is to keep always-loaded content minimal
and push everything else to mechanisms that load only when needed.

| Mechanism | Loads When | Token Cost | Use For |
|-----------|-----------|------------|---------|
| `CLAUDE.md` / `rules/*.md` (no frontmatter) | Every session | Always | Universally-applicable standing facts only |
| `rules/*.md` with `paths:` frontmatter | Matching file opened | Conditional | Language/directory-specific conventions |
| Skills | Explicitly invoked | Description only (body on demand) | Reference content, procedures, domain knowledge |
| Hooks (`settings.json`) | Tool event fires | None | Hard behavioral enforcement |

## The 200-Line Rule

Anthropic's official guidance: keep every always-loaded file under 200 lines.
Longer files cause Claude to ignore rules — important instructions get lost in
the noise. This is qualitative degradation, not just a capacity problem; it
begins before the context window fills.

**@path imports do NOT help.** `@file` references in CLAUDE.md still load the
imported content unconditionally at session start. Only `paths:` frontmatter and
skills actually reduce token spend.

## Where a New Rule Belongs

Ask these questions in order:

1. **Must this always run, regardless of whether Claude agrees?** → Hook
   (`PreToolUse` to block, `PostToolUse` to enforce after). Rules in prose have
   no compliance guarantee; hooks are deterministic.

2. **Does this only apply when working in a specific language or directory?** →
   `rules/*.md` file with `paths:` frontmatter. Example:
   ```
   ---
   paths:
     - "**/*.py"
     - "**/pyproject.toml"
   ---
   ```

3. **Is this reference content, a procedure, or domain knowledge?** → Skill.
   Skill descriptions stay in context; the full body loads only when invoked.

4. **Does this genuinely apply to every session in every project?** → Keep it in
   `CLAUDE.md` or an unconditional `rules/*.md` file. Be ruthless — if Claude
   already does it correctly without the instruction, delete it.

## The Iteration Loop (Boris Cherny / Anthropic official)

1. Run `/init` on a new project to generate a starter CLAUDE.md.
2. Treat CLAUDE.md like code: review when things go wrong, prune regularly.
3. Test each rule by removing it and observing — if behavior doesn't change,
   delete it.
4. If Claude keeps violating a rule despite it being written, the file is
   probably too long and the rule is getting lost. Move it to a hook.
5. Reserve `IMPORTANT` / `YOU MUST` emphasis for genuinely critical rules;
   overuse dilutes signal.

## Audit Checklist

When reviewing a rules file, apply each instruction to this filter:

- [ ] Is Claude violating this despite it being written? → Hook
- [ ] Does it only apply to certain file types or directories? → Add `paths:` frontmatter
- [ ] Is it a procedure or reference, not a behavioral constraint? → Skill
- [ ] Does it duplicate something Claude already does correctly? → Delete
- [ ] Is the file over 200 lines? → Prune or migrate until it isn't

## Hook Patterns for Hard Behavioral Rules

Hooks live in `settings.json` under `"hooks"`. They fire deterministically
regardless of what Claude decides.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "bash ~/.claude/hooks/guard-installs.sh"
        }]
      }
    ]
  }
}
```

A blocking hook should exit with code 2 and write a JSON decision:
```bash
echo '{"decision": "block", "reason": "Install commands are not allowed. Surface the command and let the user run it."}' >&2
exit 2
```

## Priority Moves for This Config

**Token targets:**
- Enforced gate: `audit-tokens --max-tokens 4500` (passes after work-rules restructure)
- Next gate: 2,500 — achievable via deferred items below
- Long-term target: ≤2,000 always-loaded tokens (~<200 lines, per Anthropic guidance)

**Status (2026-06-13 after work-rules restructure):** ~4,000 always-loaded tokens across
14 files (down from 7,051). Work-tree GHA, IaC, and AWS platform rules are now
path-scoped (conditional); the encrypted-dotfiles procedure rule converted to a skill pointer.

1. **Hook: never-install enforcement** — `~/.claude/hooks/guard-installs.sh` (PreToolUse
   Bash matcher). General purpose. Wire into both settings templates. Done. `audit-tokens`
   now separates always-loaded from path-scoped totals, so path-scoping a rule is reflected
   in the gated number.

2. **Path-scope `python.md`** — add `paths: ["**/*.py", "**/pyproject.toml"]` frontmatter.
   Removes 15 lines from every non-Python session. Done.

3. **Migrate `workflow.md` (107 lines) to a skill** — it is entirely procedure/reference
   ("when plan mode", "git hygiene", "session hygiene"), never a hard behavioral constraint.
   Candidate skill name: `workflow-guidance`. Keep `workflow.md` as a ~10-line stub that
   references the skill.

4. **Migrate bulky how-to lessons from `lessons.md`** — entries longer than ~10 lines
   that describe *how to do X* (git filter-repo, mailmap, XDG dirs, etc.) belong in skills.
   Keep `lessons.md` as a thin append-target with 1–2 sentence entries + `> See skill X`.
   Candidate: `git-history-surgery` skill (already exists), `xdg-conventions` skill.

5. **Audit and prune `coding.md`, `thinking.md`, `security.md`** — apply the test: "would
   removing this instruction change Claude's behavior?" Delete anything where the answer is no.
   These are currently 45, 82, 39 lines respectively — good candidates to get under 20.

6. **Path-scope work-specific rules** — Done. Work-tree GHA rules (→ `.github/`),
   IaC rules (→ `*.tf/*.hcl/iac/`), and AWS platform rules (→ `*.tf/.github/`) are now
   path-scoped. The encrypted-dotfiles procedure rule converted to a work-tree skill.
   Remaining follow-up: tighten the 2,500-token gate once `workflow.md` is migrated to a skill.

### Bottom line

- **Hooks** → behavioral enforcement (never-install, git denies, env-file guard)
- **Skills** → procedures, reference, domain knowledge
- **`paths:`-scoped rules** → language/framework/project-type conventions
- **Unconditional rules** → short, universal, things Claude would get wrong without them

## Cross-tree Ownership (chezmoiignore Pattern)

This config spans two chezmoi trees. The public koopa tree cedes ownership of
`settings.json` (and `.npmrc`, `pip.conf`) to the work tree when the generic
`~/.config/koopa/dotfiles-work` symlink exists:

```
{{- if stat (joinPath .chezmoi.homeDir ".config" "koopa" "dotfiles-work") }}
.claude/settings.json
.config/pip/pip.conf
.npmrc
{{- end }}
```

**Rules for extending this:**
- Detection key is always `dotfiles-work` (generic symlink name) — never the actual
  private repo name. This keeps the public repo free of private identifiers.
- General scripts (like `guard-installs.sh`) live in koopa and are deployed everywhere;
  both settings files merely reference them by path.
- Work-specific rules, hooks, and settings stay in the work tree. Nothing work-specific
  ever enters koopa.

## What Belongs in This Project's Setup

This user's configuration lives in chezmoi at:
```
~/.local/share/koopa/opt/dotfiles/chezmoi/dot_claude/
```
(or equivalently `~/.config/koopa/dotfiles/chezmoi/dot_claude/`).

The deployed targets are `~/.claude/`. **Always edit the chezmoi source**, not
the deployed copy — it will be overwritten on the next `chezmoi apply`.

After editing, deploy with a targeted apply:
```sh
chezmoi apply \
  --source=~/.local/share/koopa/opt/dotfiles/chezmoi \
  ~/.claude/rules/lessons.md    # or whichever file changed
```

Do NOT run `koopa configure user dotfiles` from inside a long-running agent
session — the session's `KOOPA_COLOR_MODE` may be stale and will clobber theme
files.
