# Obsidian Vault Detection

Never hardcode an Obsidian vault path; it varies by machine and person. Resolve the vault in
this order:

1. `KOOPA_BUCKET` env var (koopa's dated-notes bucket; exported on every koopa-activated shell).
2. A tool-specific override such as `OBSIDIAN_VAULT_DIR`, set in a personal shell config.
3. Obsidian's registry (`~/Library/Application Support/obsidian/obsidian.json` on macOS,
   `~/.config/obsidian/obsidian.json` on Linux): the `vaults` map of `{path, ts, open}`. Prefer
   `open: true`, else the highest `ts`.
4. No vault found: use a safe project-local default. Never hard-block.

This dotfiles repo sets no default vault path or tool-specific variable; that stays personal.
