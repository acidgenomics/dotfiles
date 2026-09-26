---
name: dotfiles-maintain-claude-config
description: >-
  Guide for maintaining and optimizing Claude Code configuration: CLAUDE.md,
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

**Never** plain `>` and **never** an inline scalar. Related constraints
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
  A correctly-formed `>-` block scalar sidesteps this: ordinary prose colons
  ("Use when: X, Y, or Z") are safe once the block-scalar form is used.
- **Name**: lowercase letters and digits joined by single hyphens, at most 64
  characters, equal to the skill's directory name, and starting with the prefix
  of the tree that owns it (see Naming and Ownership below).
- **Trigger phrase**: the description must say when to load the skill, using one
  of "Use when", "Use after", "Use before", "Use to", "Use this", or "Whenever".
  A CLI reads the description to decide when to load the skill body; without a
  trigger phrase, it has nothing to match against.
- **Body size**: about 600 lines is a soft ceiling, not a hard rule. Shrink by
  moving reference detail into a sibling file in the skill directory, not by
  summarizing it away.

Verify any skill tree with the validator (checks frontmatter shape, length,
naming, and the trigger phrase, not prose):

```sh
koopa develop check-skills                        # koopa's own default skill trees
koopa develop check-skills <path/to/skills/dir>    # any other tree, e.g. a work repo
```

Point it at a source tree (a repo's own `.claude/skills`), not at a deployed
directory shared by several trees (for example `~/.claude/skills`): the
prefix check infers each root's shared prefix by majority, so a minority
tree's skills would be flagged as outliers there.

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

## Slimming a Bloated Lessons File (migration pattern)

When a project lessons file (`<prefix>-lessons.md`, or `lessons.md` if the
repo does not prefix its rules) exceeds ~200 lines, apply this triage to
each lesson:

1. **Subsystem gotcha / how-to reference** → fold the full content verbatim into
   the owning skill's `## Gotchas` section (or a similarly named topical
   heading, matching that skill's own convention). Replace the lessons-file
   entry with a 1-line pointer: `- **Title**: see the \`skill-name\` skill.`
2. **Path-bound lesson** (fires only when a matching file is open) → move it
   into the matching path-scoped rule instead. No pointer is needed; the rule
   loads on its own when that file opens.
3. **Universal behavioral rule** (short, fires without a specific file open) →
   keep in the lessons file, trimmed to 1 or 2 sentences.
4. Never delete institutional knowledge, only move it to the skill or rule that
   owns the subsystem. If neither exists, keep it (trimmed) in the lessons file.

Do not keep a skills index or a path-scoped-rules index table in an
always-loaded file. Claude Code already lists every skill's description, and
it already loads a `paths:`-scoped rule on its own when a matching file
opens, so an index in `CLAUDE.md` or the lessons file only repeats what the
tool itself already surfaces, at always-loaded token cost.

This pattern routinely achieves 70-80% token reduction on a bloated lessons
file while preserving all knowledge in skill files that load on-demand.

## Priority Moves for This Config

**Token targets:**
- Global always-loaded: ~2,161 tokens (stable)
- Any project `lessons.md`: ≤200 lines / ≤3,000 tokens
- Combined (global + project): target ≤8,000 tokens

### Completed moves

1. **Hook: never-install enforcement**: `~/.claude/hooks/guard-installs.sh`. Done.

2. **Path-scope `dotfiles-python.md`**: `paths: ["**/*.py", "**/pyproject.toml"]`. Done.

3. **Path-scope environment-specific rules**: GHA, IaC, cloud-platform rules
   path-scoped to their relevant file patterns. Done.

4. **Migrate bulky lessons-file entries to skills**: apply the triage pattern above
   whenever a project lessons file exceeds 200 lines.

5. **Migrate `dotfiles-workflow.md` to a skill**: it was entirely procedure and
   reference, never a hard behavioral constraint. Now a ~10-line stub with a
   pointer to the `dotfiles-workflow-guidance` skill. Done.

### Remaining items

6. **Audit and prune `dotfiles-coding.md`, `dotfiles-thinking.md`, `dotfiles-security.md`**:
   apply the test, "would removing this instruction change Claude's behavior?"
   Delete where the answer is no.

### Bottom line

- **Hooks**: behavioral enforcement (never-install, git denies, env-file guard)
- **Skills**: procedures, reference, domain knowledge
- **`paths:`-scoped rules**: language/framework/project-type conventions
- **Unconditional rules**: short, universal, things Claude would get wrong without them

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

## Naming and Ownership

Every file this tree deploys into `~/.claude/rules/` or `~/.claude/skills/` must
carry a prefix that names the tree that owns it. The prefix stops two trees from
silently writing to the same bare filename.

| Layer | Location | Owner | Prefix |
|---|---|---|---|
| User-global, public | `~/.claude/{rules,skills}/` | this public dotfiles tree (main tree) | `dotfiles-` |
| User-global, other private/work trees | same directories | that tree's own install | its own distinct prefix (not `dotfiles-`) |
| Project | `<repo>/.claude/{rules,skills}/` | that repo | `<repo-name>-`, e.g. `koopa-` |
| Project lessons file | `<repo>/.claude/rules/<repo-name>-lessons.md`, or `lessons.md` if the repo does not prefix its rules | that repo | the repo's own prefix, if it has one |
| Local, unmanaged | any unprefixed name under `~/.claude/` | the user, not any managed tree | none |

**The invariant:** a managed tree must only ever deploy files whose name carries
its own prefix into `~/.claude/rules/` or `~/.claude/skills/`. This is what keeps
two trees, or a tree and the user, from silently colliding on the same bare
filename.

This tree's prefix is `dotfiles-`, not something like `personal-`, because the
prefix names the tree or repo that owns and deploys the file. This tree is the
shared public dotfiles repo, not a personal one, so `dotfiles-` is correct where
`personal-` would not be.

`.chezmoiremove` may list an unprefixed legacy filename only for a one-time
migration off an old, no-longer-prefixed name. It is never an ongoing pattern:
remove the entry once the migration lands.

## See also

- `dotfiles-claude-permissions` — protected paths, permission modes, allow/ask/deny
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
  ~/.claude/rules/dotfiles-lessons.md    # or whichever file changed
```

Do NOT run `koopa configure user dotfiles` from inside a long-running agent
session — the session's `KOOPA_COLOR_MODE` may be stale and will clobber theme
files.
