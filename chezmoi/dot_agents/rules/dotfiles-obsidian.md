# Obsidian Vault Detection

No project should assume a single, hardcoded Obsidian vault path. Vault
name and location vary by machine and by person; a tool that hardcodes one
breaks the moment it runs somewhere else.

Prefer this resolution order for any tool that wants to write into "the"
Obsidian vault:

1. `KOOPA_BUCKET` env var — koopa's own general "dated notes bucket"
   concept. `_koopa_activate_today_bucket` (koopa's own activation,
   `lang/{sh,bash,zsh,fish}/functions/activate/`) resolves and exports this
   automatically on every koopa-activated shell once it finds a bucket dir
   (`KOOPA_BUCKET` itself, else `~/bucket`, else `~/Documents/bucket`).
   Anyone using koopa gets this for free, no per-project config needed.
2. A narrower, tool-specific env var override (e.g. `OBSIDIAN_VAULT_DIR`) —
   set this yourself in a personal, non-shared shell config for a vault
   that differs from your koopa bucket, or if you don't use koopa at all.
3. Auto-detect from Obsidian's own vault registry
   (`~/Library/Application Support/obsidian/obsidian.json` on macOS,
   `~/.config/obsidian/obsidian.json` on Linux) — a JSON `vaults` map keyed
   by vault id, each entry `{path, ts, open}`. Prefer the vault marked
   `open: true`; fall back to the highest `ts` (most recently used) if none
   is open.
4. No vault detected — fall back to a safe, project-local default. Never
   hard-block on the absence of a vault.

This repo's own `dot_config/homebrew/Brewfile.tmpl` installs the `obsidian`
cask; nothing here sets a default vault path or tool-specific env var —
that stays a personal choice, made in your own shell config, not baked
into dotfiles. `KOOPA_BUCKET` is the one exception, and it comes from
koopa's own activation, not from this dotfiles repo.
