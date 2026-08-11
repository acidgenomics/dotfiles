---
name: maintain-claude-config
description: >-
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

## SKILL.md Frontmatter Format (Cross-CLI Compatibility)

Every skill's `description:` key must use the folded-strip block scalar:

```yaml
description: >-
  One or more lines of prose describing what the skill covers and when to use it.
```

**Never** plain `>` and **never** an inline scalar. Two related constraints
(Claude Code itself has no such limit, but a skill tree shared across tools must
satisfy every reader):

- **Length**: keep the raw description text ≤1023 chars. The 1024-char cap on the
  *parsed* description is a constraint of the open Agent Skills spec itself
  (agentskills.io) — Codex CLI hardcodes the same `MAX_DESCRIPTION_LEN=1024`, and
  Copilot CLI enforces it too. An over-cap skill gets dropped by whichever CLI
  reads it (Copilot CLI's current behavior is a per-skill drop with a "N skill(s)
  failed to load" banner, not the whole-directory failure earlier Copilot versions
  had). `>-` makes parsed length equal raw length; plain `>` folds in a trailing
  newline, silently spending 1 char of the budget for nothing.
- **Avoid stray `key: value` patterns inside the description body.** A naive
  non-block-scalar extractor can misread a colon-space as a nested YAML mapping.
  A correctly-formed `>-` block scalar sidesteps this — ordinary prose colons
  ("Use when: X, Y, or Z") are safe once the block-scalar form is used.

Verify any skill tree with the validator (checks frontmatter shape and length,
not prose):

```sh
koopa develop check-skills                        # koopa's own two skill trees
koopa develop check-skills <path/to/skills/dir>    # any other tree, e.g. a work repo
```

### Cross-CLI discovery: the `.agents/skills` convention

The Agent Skills format is an open standard (originally from Anthropic,
spec at agentskills.io) that Codex CLI, Gemini CLI, and Copilot CLI all read
directly — same `SKILL.md` files, no format changes needed beyond the frontmatter
rules above. Each tool also honors a shared `.agents/skills` alias directory in
addition to its own native path:

| Tool | Native path(s) | Also honors `.agents/skills`? |
|---|---|---|
| Claude Code | `.claude/skills/`, `~/.claude/skills/` | n/a (this is the source) |
| Codex CLI | `.codex/skills/` (walking up to repo root), `~/.codex/skills/` | Yes |
| Gemini CLI | `.gemini/skills/`, `~/.gemini/skills/` | Yes — wins over `.gemini/skills` at the same tier |
| Copilot CLI | `.github/skills/`, `.claude/skills/`, `~/.copilot/skills/` | Yes |
| Antigravity CLI (`agy`) | Unconfirmed — no public doc page found; changelog confirms native skill support exists | Unconfirmed — no evidence either way |

Both this repo's `.agents/skills` (git-tracked symlink → `.claude/skills/`) and the
user-global `~/.agents/skills` (chezmoi-managed symlink → `~/.claude/skills/`,
source `dot_agents/symlink_skills.tmpl`) already exist, so Codex, Gemini CLI, and
Copilot CLI all see this skill tree with zero extra work. Antigravity is an
accepted gap, not a pending task: its config root is `~/.gemini/config/`, not
`~/.gemini/skills/`, and confirming its exact skill-discovery path requires an
authenticated `agy` session — this machine has no Antigravity login, so the path
stays unverified here. Re-check only if Antigravity auth becomes available.

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

## Auditing Token Usage with `koopa app claude audit-tokens`

The command reports approximate token cost for always-loaded Claude config.
Token estimate: `len(text) // 4` (chars, not bytes).

**Flags:**
- `--scope {all,global,project}` — default `all`; scan global `~/.claude/`, the
  current project's `.claude/`, or both. Project root is auto-discovered by walking
  up from CWD looking for a `.claude/` subdir or `.git/`.
- `--project-dir PATH` — explicit project root, skips CWD discovery.
- `--max-tokens N` — exit 1 if combined always-loaded tokens exceed N.

**What "always-loaded" means:** `CLAUDE.md` + all `rules/**/*.md` files without
`paths:` frontmatter. Path-scoped files are reported separately but excluded from
the gated total.

The combined `all` output is the true per-session token cost before the first prompt.
Use `--scope global` to see only the global `~/.claude/` tree (pre-2026-07 behavior).

## Slimming a Bloated `lessons.md` (migration pattern)

When a project `lessons.md` exceeds ~200 lines, apply this triage to each lesson:

1. **Subsystem gotcha / how-to reference** → fold the full content verbatim into
   the matching skill under a `## Lessons (Migrated from rules/lessons.md)` section.
   Replace the lessons.md entry with a 1-line pointer:
   `- **Title** → see \`skill-name\` skill.`
2. **Universal behavioral rule** (short, fires without a specific file open) →
   keep in lessons.md, trimmed to 1–2 sentences.
3. Never delete institutional knowledge — only move it to the skill that owns the
   subsystem. If no matching skill exists, keep it (trimmed) in lessons.md.

This pattern routinely achieves 70–80% token reduction on a bloated lessons.md
while preserving all knowledge in skill files that load on-demand.

## Priority Moves for This Config

**Token targets:**
- Global always-loaded: ~2,161 tokens (stable)
- Any project `lessons.md`: ≤200 lines / ≤3,000 tokens
- Combined (global + project): target ≤8,000 tokens

### Completed moves

1. **Hook: never-install enforcement** — `~/.claude/hooks/guard-installs.sh`. Done.

2. **Path-scope `python.md`** — `paths: ["**/*.py", "**/pyproject.toml"]`. Done.

3. **Path-scope environment-specific rules** — GHA, IaC, cloud-platform rules
   path-scoped to their relevant file patterns. Done.

4. **Migrate bulky `lessons.md` entries to skills** — apply the triage pattern above
   whenever a project lessons.md exceeds 200 lines.

### Remaining items

5. **Migrate `workflow.md` (107 lines) to a skill** — entirely procedure/reference,
   never a hard behavioral constraint. Keep as a ~10-line stub + skill pointer.

6. **Audit and prune `coding.md`, `thinking.md`, `security.md`** — apply the test:
   "would removing this instruction change Claude's behavior?" Delete where no.

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

## See also

- `claude-permissions` — protected paths, permission modes, allow/ask/deny
  precedence, PreToolUse `permissionDecision` contract, and the carve-out hook
  for `.claude/` writes. Use when debugging unexpected permission prompts.

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
