#!/usr/bin/env bash
# PreToolUse hook: block software install commands.
# Covers language package managers, system package managers, koopa, and network installers.
# Fail-OPEN: infrastructure errors defer to normal permission flow (exit 0, no output).
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[[ -z "$cmd" ]] && exit 0

# Each pattern is anchored to avoid partial hits (e.g. "reinstall" or "uninstall").
# Word boundary: preceded by start-of-string, space, semicolon, pipe, or &&/||.
_matches_install() {
  local c="$1"
  # Language package managers
  [[ "$c" =~ (^|[[:space:];|&])(pip|pip3)[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])python[[:space:]]+-m[[:space:]]+pip[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])uv[[:space:]]+(add|pip[[:space:]]+install)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])pipx[[:space:]]+(install|upgrade)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])(npm)[[:space:]]+(install|i|update|add)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])(pnpm|yarn)[[:space:]]+(install|add|update)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])poetry[[:space:]]+add([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])gem[[:space:]]+(install|update)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])cargo[[:space:]]+(install|update)([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])go[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])(cpan|cpanm)[[:space:]] ]] && return 0
  # R package managers
  [[ "$c" =~ install\.packages\( ]] && return 0
  [[ "$c" =~ (BiocManager|renv)::install\( ]] && return 0
  # System package managers
  [[ "$c" =~ (^|[[:space:];|&])brew[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])(apt|apt-get)[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])(dnf|yum)[[:space:]]+install([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])pacman[[:space:]]+-S([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:];|&])port[[:space:]]+install([[:space:]]|$) ]] && return 0
  # koopa installer
  [[ "$c" =~ (^|[[:space:];|&])koopa[[:space:]]+install([[:space:]]|$) ]] && return 0
  # Network/bootstrap installers piped to shell
  [[ "$c" =~ \|[[:space:]]*(bash|sh|zsh)([[:space:]]|$) ]] && [[ "$c" =~ (curl|wget)[[:space:]] ]] && return 0
  return 1
}

if _matches_install "$cmd"; then
  printf '%s\n' '{"decision":"block","reason":"Software installs are not allowed. Surface the command or koopa app name and let the user install it."}' >&2
  exit 2
fi

exit 0
