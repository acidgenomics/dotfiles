# Obsidian Vault Detection

Never hardcode an Obsidian vault path; it varies by machine and person. Resolve the vault in
this order:

1. `obsidian vault info=path`: prints only the active vault's path. With several vaults
   (`obsidian vaults verbose`), pass `vault=<name>` or ask. Ask Obsidian itself first; an
   environment variable can be stale or point at a different path than the vault Obsidian opens.
2. Obsidian's registry, if the CLI is unavailable (`~/Library/Application Support/obsidian/obsidian.json`
   on macOS, `~/.config/obsidian/obsidian.json` on Linux): the `vaults` map of `{path, ts, open}`.
   Prefer `open: true`, else the highest `ts`.
3. Last resort only: a tool-specific override such as `OBSIDIAN_VAULT_DIR` (set in a personal shell
   config), then `KOOPA_BUCKET` (koopa's dated-notes bucket; exported on every koopa-activated shell).
4. No vault found: use a safe project-local default. Never hard-block.

This dotfiles repo sets no default vault path or tool-specific variable; that stays personal.
