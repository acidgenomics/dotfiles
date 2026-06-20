#!/usr/bin/env bash
# PreToolUse hook: block broad filesystem scans rooted at home or system root.
# A scan is "broad" when its root is ~, $HOME, /, /Users, /home, or a bare home
# directory (/Users/<name> or /home/<name> with no further subpath).
# Scans rooted in deeper project subdirectories are allowed.
# Fail-OPEN: infrastructure errors defer to normal permission flow (exit 0, no output).
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null) || exit 0
[[ -z "$cmd" ]] && exit 0

# Returns 0 (block) when the path is a home alias or system-level root.
# Allows deeper subdirectories: /Users/name/.local/share/... → not broad.
_is_broad_root() {
  local raw="$1"
  # Strip trailing slash, but preserve bare / and ~/
  local p
  if [[ "$raw" == '/' || "$raw" == '~/' ]]; then
    p="$raw"
  else
    p="${raw%/}"
  fi
  case "$p" in
    # shellcheck disable=SC2016  # $HOME/${ HOME} are literal strings to match, not expansions
    '~' | '~/' | '$HOME' | '${HOME}' | '/') return 0 ;;
    '/Users' | '/home') return 0 ;;
    /Users/*)
      # Broad only if there is no further subpath after the name segment
      local rest="${p#/Users/}"
      [[ "$rest" != */* ]] && return 0
      return 1
      ;;
    /home/*)
      local rest="${p#/home/}"
      [[ "$rest" != */* ]] && return 0
      return 1
      ;;
    *) return 1 ;;
  esac
}

# Check all non-flag tokens in the command; return 0 if any is a broad root.
# Used for grep/rg/fd where the path is a positional argument.
_has_broad_path_token() {
  local c="$1"
  local -a words
  read -ra words <<< "$c"
  local w
  for w in "${words[@]}"; do
    case "$w" in
      -* | '') continue ;;
      *) _is_broad_root "$w" && return 0 ;;
    esac
  done
  return 1
}

_matches_broad_scan() {
  local c="$1"
  local pat tok root

  # ── find ──────────────────────────────────────────────────────────────────
  # Extract the search root: first non-flag arg after 'find', skipping -H/-L/-P.
  pat='(^|[[:space:]])find[[:space:]]'
  if [[ "$c" =~ $pat ]]; then
    local after="${c#*find }"
    local -a find_words
    read -ra find_words <<< "$after"
    root=''
    for tok in "${find_words[@]}"; do
      case "$tok" in
        -H | -L | -P) continue ;;
        -*) break ;;
        *) root="$tok"; break ;;
      esac
    done
    [[ -n "$root" ]] && _is_broad_root "$root" && return 0
  fi

  # ── grep -r / -R ──────────────────────────────────────────────────────────
  pat='(^|[[:space:]])grep[[:space:]]+-[a-zA-Z]*[rR]'
  if [[ "$c" =~ $pat ]]; then
    _has_broad_path_token "$c" && return 0
  fi

  # ── rg (ripgrep, recursive by default) ────────────────────────────────────
  pat='(^|[[:space:]])rg[[:space:]]'
  if [[ "$c" =~ $pat ]]; then
    _has_broad_path_token "$c" && return 0
  fi

  # ── fd / fdfind ───────────────────────────────────────────────────────────
  pat='(^|[[:space:]])(fd|fdfind)[[:space:]]'
  if [[ "$c" =~ $pat ]]; then
    _has_broad_path_token "$c" && return 0
  fi

  return 1
}

if _matches_broad_scan "$cmd"; then
  printf '%s\n' '{"decision":"block","reason":"Broad filesystem scan blocked. Scope the search to the project directory or a known subpath — not the home directory or system root. Ask the user if a wider scan is genuinely needed."}' >&2
  exit 2
fi

exit 0
