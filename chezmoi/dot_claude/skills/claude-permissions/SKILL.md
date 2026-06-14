---
name: claude-permissions
description: >
  Claude Code permission system internals — protected paths, permission modes,
  allow/ask/deny rule precedence, and the PreToolUse permissionDecision hook
  contract. Use when debugging unexpected permission prompts, understanding why
  Edit(.claude/**) or Bash(*) allow rules have no effect on .claude/ writes,
  or reasoning about acceptEdits vs plan vs bypassPermissions mode tradeoffs.
---

# Claude Code Permission System

## Evaluation model

Permission modes set the **baseline**. Rules layer on top in order `deny → ask →
allow`. The first match wins; specificity does not change the order. Allow rules
cannot expand beyond the mode's capability boundary.

```
[mode baseline] → deny → ask → allow → default for unmatched
```

A matching `ask` rule still prompts even when a more specific `allow` rule also
matches the same call. A `PreToolUse` hook that exits with code 2 blocks before
rules are evaluated, so a blocking hook wins over an allow rule.

## Permission modes

| Mode | What runs without asking | Notes |
|---|---|---|
| `default` | Reads only | Prompts on first tool use |
| `acceptEdits` | Reads + file edits + common filesystem Bash† | See detail below |
| `plan` | Reads only | Same prompting as default; blocks edits by design |
| `auto` | Everything (background classifier) | Research preview |
| `dontAsk` | Only pre-approved tools | Non-interactive; ask rules are denied |
| `bypassPermissions` | Everything | Isolated containers/VMs only |

† `acceptEdits` Bash auto-approvals: `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`,
`sed` — for paths inside the working directory or `additionalDirectories` only.
Protected paths (see below) still prompt in every mode except `bypassPermissions`.

## Protected paths — the key insight

**Writes to protected paths are never auto-approved in any mode except
`bypassPermissions`.** `permissions.allow` rules do NOT pre-approve them — the
safety check runs *before* allow-rule evaluation. An entry like `Edit(.claude/**)`
in `settings.json` has no effect on the per-mode outcome table.

In modes that prompt, the dialog offers **"Yes, and allow Claude to edit its own
settings for this session"** — a per-session approval that covers subsequent writes
without further prompting (file edits only; does not cover Bash `mkdir`).

### Per-mode behavior for protected paths

| Mode | Protected-path write |
|---|---|
| `default`, `acceptEdits`, `plan` | Prompted |
| `auto` | Routed to classifier |
| `dontAsk` | Denied |
| `bypassPermissions` | Allowed |

### Protected directories

- `.git`
- `.config/git`
- `.vscode`
- `.idea`
- `.husky`
- `.cargo`
- `.devcontainer`
- `.yarn`
- `.mvn`
- `.claude` (except `.claude/worktrees`)

### Protected files

`.gitconfig`, `.gitmodules`; shell rc/profile files (`.bashrc`, `.zshrc`,
`.zprofile`, `.zshenv`, `.zlogin`, `.zlogout`, `.profile`, `.envrc`, etc.);
package manager configs (`.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.pnpmfile.cjs`,
`bunfig.toml`, etc.); build tool configs (`.bazelrc`, `.bazelversion`, etc.);
hook configs (`.pre-commit-config.yaml`, `lefthook.yml`, etc.); `.mcp.json`,
`.claude.json`, `pyrightconfig.json`, `.ripgreprc`.

## Escape hatches (ranked by practicality)

1. **Per-session click** — "Yes, and allow Claude to edit its own settings for this
   session." One click per session; covers file edits only (not Bash `mkdir`).
   This is the only reliable in-session option short of `bypassPermissions`.
2. **`bypassPermissions` mode** — skips all protected-path prompts. Too broad for
   general use; suitable only in isolated containers/VMs.

## PreToolUse hook permissionDecision contract

The hook writes JSON to stdout and exits 0:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "permissionDecisionReason": "reason string (shown only on deny)"
  }
}
```

| Value | Effect |
|---|---|
| `"allow"` | Skips the permission prompt; tool call proceeds |
| `"deny"` | Blocks the call; reason shown to user |
| `"ask"` | Forces a prompt regardless of allow rules |
| `"defer"` | Passes to normal permission flow (same as no output) |

Exit code 2 (+ stderr) blocks the tool call *before* rules are evaluated — a
blocking hook wins even when an allow rule would otherwise pass.

Hook decisions do **not** bypass `deny` or `ask` rules — those are still evaluated
after the hook. A matching `deny` rule blocks even when the hook returned `"allow"`.

### ✗ Verified (Claude Code 2.1.177, Bedrock): hook `allow` does NOT override the protected-path gate

Tested empirically with three headless `claude -p --permission-mode acceptEdits`
probes from a real project root (koopa, 2026-06-14):

| Probe | Protected? | Hook | File created? |
|---|---|---|---|
| `_probe_normal_DELETEME.md` (repo root) | no | n/a | ✓ (positive control) |
| `.claude/rules/_probe_DELETEME.md` | yes | `allow` emitted | ✗ — still prompted |
| `.claude/_probe_DELETEME.md` | yes | defer | ✗ (expected) |

**Conclusion:** A `PreToolUse` hook returning `permissionDecision: "allow"` does not
suppress the protected-path prompt. The safety check runs outside the hook's reach.
`permissions.allow` rules and hooks are both ineffective. The per-session click
("Yes, and allow Claude to edit its own settings for this session") is the only
config-level escape hatch for file edits. There is no workaround for Bash `mkdir`
into `.claude/`.

The `guard-claude-allow.sh` hook deployed on this machine (`~/.claude/hooks/`) is
**ineffective for protected-path writes**. It correctly emits `allow` JSON (unit
tests pass), but Claude Code ignores that decision for protected paths. The hook
can be left in place harmlessly or removed — it provides no benefit for `.claude/`
writes.

## See also

- `maintain-claude-config` — where a new rule/hook/skill belongs; token budgets;
  the two-tree chezmoi ownership model for `~/.claude`.
