# Dotfiles

![Lifecycle: stable](https://img.shields.io/badge/lifecycle-stable-brightgreen.svg)
![License: Apache-2.0](https://img.shields.io/github/license/acidgenomics/dotfiles)

[Acid Genomics][] configuration files managed with [chezmoi][] via the [koopa][]
shell framework.

## About

[Koopa][] is a POSIX-compliant shell bootloader that provides consistent
developer tooling across macOS and Linux. It manages software installation,
shell configuration, and dotfiles as a unified system.

## Installation

Install koopa first by following the [koopa documentation][koopa]. Then install
and configure these dotfiles:

```sh
koopa install dotfiles
koopa configure user dotfiles
```

This clones the repo, runs the installer (which sets up Dracula Pro themes if
available at `~/.local/share/dracula-pro/`), and applies chezmoi templates to
your home directory.

## How it works

Config files live in `chezmoi/` as Go templates (`.tmpl` suffix). Running
`chezmoi apply` renders them into your home directory with machine-specific
values substituted at apply time.

Key environment variables that control template output:

| Variable | Values | Default |
|----------|--------|---------|
| `KOOPA_COLOR_MODE` | `dark`, `light` | auto-detected (macOS) or `dark` (Linux) |
| `KOOPA_DRACULA_PRO_VARIANT` | `pro`, `blade`, `buffy`, `lincoln`, `morbius`, `van-helsing` | `pro` |
| `KOOPA_PREFIX` | path | `~/.local/share/koopa` |

Apps that support runtime theme switching (tmux, neovim, dircolors) read
`KOOPA_COLOR_MODE` directly at startup rather than relying on `chezmoi apply`.

## Color themes

These dotfiles use [Dracula Pro][] with automatic dark/light mode switching.

**Auto-detection**: On macOS, `KOOPA_COLOR_MODE` is derived from the system
appearance setting at shell startup. On Linux, it defaults to `dark`.

**Manual override**: To switch modes, set the variable and re-apply:

```sh
export KOOPA_COLOR_MODE="light"
chezmoi apply
```

**Dracula Pro variants**: Set `KOOPA_DRACULA_PRO_VARIANT` to one of the palette
names (`blade`, `buffy`, `lincoln`, `morbius`, `van-helsing`, or the default
`pro`).

**Fallback themes**: Without Dracula Pro installed at
`~/.local/share/dracula-pro/`, configs use the free [Dracula][] theme (dark) or
Atom One Light / OneHalfLight (light).

**Supported apps** (via chezmoi templates):

- *Terminal emulators*: Alacritty, Ghostty, Hyper, kitty, WezTerm
- *Editors*: Cursor, Doom Emacs, neovim, Positron, RStudio, vim, VS Code, Zed
- *CLI tools*: bat, bottom, cheat, delta, fzf, htop, McFly, neofetch, ranger, ripgrep, starship
- *Shells*: bash, elvish, fish, nushell, PowerShell, zsh
- *Other*: IPython, radian, tmux

## See also

- [GitHub does dotfiles](https://dotfiles.github.io/)
- [Dracula Pro][]
- [chezmoi documentation][chezmoi]

## License

Apache-2.0 — Copyright 2016 Acid Genomics LLC — see [LICENSE](LICENSE).

[acid genomics]: https://acidgenomics.com/
[chezmoi]: https://www.chezmoi.io/
[dracula]: https://draculatheme.com/
[dracula pro]: https://draculatheme.com/pro
[koopa]: https://koopa.acidgenomics.com/
