---
name: koopa-chezmoi-dotfiles
description: >
  How koopa manages home dotfiles via chezmoi — source-of-truth layout, the
  explicit --source flag, template-vs-generator ordering, XDG path derivation in
  templates, and the correct re-run command. Use when editing a dotfile, working
  in opt/dotfiles/chezmoi/, debugging a file that reverts on chezmoi apply, or
  wiring a chezmoi template.
---

# koopa Chezmoi Dotfiles

## Source of Truth

The chezmoi source root is:
```
~/.local/share/koopa/opt/dotfiles/chezmoi/
```

**`~/.local/share/chezmoi` must not exist.** Chezmoi is always invoked with an
explicit `--source=<opt/dotfiles>/chezmoi` flag. If `~/.local/share/chezmoi` exists,
it was created accidentally — warn and remove it (after confirming it is not user
data). A bare `chezmoi apply` without `--source` would deploy `dot_*` files into
`~/chezmoi/` instead of `~/`, which is wrong.

**Never run `chezmoi apply` without `--source`** pointing at `opt/dotfiles/chezmoi/`.

## Always Edit the Source First

Home-directory dotfiles are managed by chezmoi. The deployed copies under `~/` will
be overwritten on the next `chezmoi apply`.

**Always edit the chezmoi source file.** When a task touches a deployed dotfile
(e.g. `~/.config/nvim/lua/plugins/treesitter.lua`), immediately locate and edit the
corresponding source file (e.g.
`~/.local/share/koopa/opt/dotfiles/chezmoi/dot_config/nvim/lua/plugins/treesitter.lua`).
Do not treat the deployed copy and the source as two separate steps.

After editing, deploy with a targeted apply:
```sh
chezmoi apply \
  --source=~/.local/share/koopa/opt/dotfiles/chezmoi \
  ~/.config/nvim/lua/plugins/treesitter.lua   # whichever file(s) changed
```

**Do NOT run `koopa configure user dotfiles` from inside a long-running agent session**
— the session's `KOOPA_COLOR_MODE` may be stale and will clobber theme files. See
skill `koopa-color-mode`.

## Re-Run Command

To re-run the full dotfiles installer:
```sh
koopa configure user dotfiles
```
NOT `koopa configure-dotfiles` (that command does not exist).

## Templates Run Before Post-Install Generators

Chezmoi templates execute **before** any post-install generator runs. When a template
needs to detect something that a post-chezmoi function generates (e.g. a `.rstheme`
file generated from an upstream `.tmTheme`), `stat` on the generated output will
always miss at template render time.

Instead, detect the **source** that triggers generation (e.g. the upstream `.tmTheme`
file itself) rather than the generated artifact.

## XDG Paths in Chezmoi Templates

chezmoi has no native XDG variables. Use:
```
{{- $dataHome := env "XDG_DATA_HOME" | default (joinPath .chezmoi.homeDir ".local/share") -}}
{{- $configHome := env "XDG_CONFIG_HOME" | default (joinPath .chezmoi.homeDir ".config") -}}
```

The `.chezmoi.homeDir` fallback is the XDG spec definition — unavoidable and correct.

In standalone scripts (no `koopa` import), inline:
```python
xdg_config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
xdg_data_home = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
```

Never confuse `XDG_DATA_HOME` (single writable user data dir) with `XDG_DATA_DIRS`
(colon-separated read-only system search path). Never derive a write/install location
from `XDG_DATA_DIRS`.
