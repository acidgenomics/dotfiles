# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed

- Migrated bat, delta, kitty, and bottom from static dark/light variant files
  to chezmoi templates; symlink-based color switching is fully removed
- Kitty uses Atom One Light as the light fallback theme

## 2025-05

### Added

- Dracula Pro theme support for BBEdit, JetBrains IDEs, Notepad++, Raycast,
  and Sublime Text
- Claude AI settings, rules, and hook configuration

### Changed

- Improved theme consistency across all supported apps for both dark and light modes
- Improved Dracula Pro configuration handling for neovim and RStudio
- Switched to native Python REPL (from IPython default)
- Disabled GitHub Copilot by default in VS Code / Positron
- Reworked spacemacs and vim/neovim configurations

## 2025-03

### Added

- Positron IDE support
- Air formatter integration for RStudio

### Changed

- Hardened default type checking settings
- Improved neovim LSP and completion configuration

## 2025-01

### Added

- WezTerm terminal emulator config with color switching
- McFly color configuration for light mode

### Changed

- Improved tmux config
- Disabled ligatures in WezTerm
- Set default shell to bash in terminal emulators
- Disabled `GLOBAL_RCS` for zsh

## 2024-11

### Added

- Proxy server support for wget, npm, pip, and curl
- Custom CA certificate file support (`AWS_CA_BUNDLE`)

## 2024-09

### Added

- Positron IDE settings
- rclone S3 configuration
- VS Code Server config

### Changed

- Reworked bash and zsh shell configs
- Improved conditional configuration for personal vs. work repos

## 2024-06

### Added

- Initial chezmoi-managed dotfiles with dark/light color mode switching
- Dracula Pro theme support across terminal emulators, editors, and CLI tools
- KOOPA_COLOR_MODE auto-detection from macOS system appearance
