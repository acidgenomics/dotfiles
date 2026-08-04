---
paths:
  - "**/*.sh"
  - "**/*.bash"
  - "**/*.zsh"
  - "**/executable_*"
  - "**/dot_*profile*"
  - "**/dot_*rc*"
  - "**/dot_aliases*"
  - "**/dot_z*"
  - "**/*.tmpl"
  - "**/install"
---

# Shell / Bash Conventions

## Indentation

Always use 4-space indentation — never 2 spaces. This applies to all levels:
function bodies, `if`/`for`/`while` blocks, `case` branches, and nested constructs.

The `dot_*`/`executable_*`/`*.tmpl` globs above exist because chezmoi source
files carry filename prefixes/suffixes instead of a `.sh` extension — a plain
`**/*.sh` glob matches none of them. `**/*.tmpl` is deliberately broad and also
catches non-shell templates (JSON, YAML, TOML config); this rule governs shell
indentation only — data-format templates follow the `.editorconfig` 2-space
sections instead.
