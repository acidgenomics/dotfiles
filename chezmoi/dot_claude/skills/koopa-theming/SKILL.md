---
name: koopa-theming
description: >
  Reference for koopa theme synthesis across editors and terminals — JetBrains/
  IntelliJ scheme delivery, runtime palette derivation, atuin and mcfly color
  config, and macOS sandboxed-app theme installation. Use when generating or fixing
  editor/terminal color schemes, debugging a theme that renders incorrectly, or
  writing theme-install code. For the "never hardcode Pro hex" guardrail see the
  path-scoped theme-colors rule.
---

# koopa Theming Reference

## Dracula Pro: Runtime Derivation Architecture

Proprietary paid-theme hex values (Dracula Pro, Dracula Pro Alucard) must **never**
appear as literals in any tracked file — derive them at runtime only.

**Allowed as literals:**
- Free Dracula OSS colors: `#282a36`, `#6272a4`, `#50fa7b`, `#f1fa8c`, `#ff79c6`,
  `#bd93f9`, `#8be9fd`, `#ffb86c`, `#ff5555`
- Generic neutrals: `#ffffff`, `#000000`, `#fafafa`, plain greys

**Correct architecture:**
1. Install script reads colors via `_parse_ghostty_palette(dp_dir, variant)` from
   `~/.local/share/dracula-pro/themes/ghostty/<variant>`.
2. Generates palette files outside the chezmoi tree (e.g.
   `~/.config/zsh/dracula-pro-colors.zsh`, `~/.config/fish/dracula-pro-colors.fish`).
3. Chezmoi templates source/include those generated files at runtime with a fallback
   to free Dracula OSS colors when the generated file does not exist:

```toml
{{- if stat (joinPath .chezmoi.homeDir ".config/starship/dracula-pro.toml") }}
{{- include (joinPath .chezmoi.homeDir ".config/starship/dracula-pro.toml") }}
{{- else }}
purple = "#bd93f9"
{{- end }}
```

**Before writing any hex into a tracked file:**
```sh
grep -iE '<THE_HEX>' ~/.local/share/dracula-pro/themes/ghostty/pro
```
If it matches, the code must read it at runtime.

## JetBrains Editor Scheme Synthesis

### IntelliJ config-dir shadowing

IntelliJ gives `<config>/colors/*.xml` **priority over plugin-bundled schemes of the
same name**. A stale config-dir file silently wins even when the plugin jar has correct
colors.

**Fix pattern:** when switching from config-dir scheme delivery to plugin-bundled, add
cleanup to remove stale files before installing the plugin:

```python
for stale in (
    os.path.join(ide_dir, "colors", "SchemeName.xml"),
    os.path.join(ide_dir, "themes", "SchemeName.theme.json"),
):
    if os.path.isfile(stale):
        os.remove(stale)
```

### Runtime substitution map

Build the dark→light substitution map entirely at runtime — never hardcode map keys
or values:

- **Keys**: `_parse_ghostty_palette(dp_dir, "<dark-variant>")` — parsed from local
  vendor source.
- **Values**: `_parse_ghostty_palette(dp_dir, "<light-variant>")`, aligned by ANSI
  index. Non-ANSI roles (orange, etc.) from the Fleet experimental palette JSON at
  `~/.local/share/<theme>/themes/jetbrains/experimental/fleet/`.
- Tokens with no named-palette equivalent: lightened algorithmically via
  luminance-flip (`colorsys`).

**Mandatory verification asserts (add permanently in the synthesis function):**

```python
# No dark tokens survived substitution
survivors = {t.lower() for t in re.findall(r'value="([0-9A-Fa-f]{6})"', xml)} & set(named_map)
assert not survivors, f"Dark tokens survived: {sorted(survivors)}"

# All background values are light (luminance ≥ 0.55)
for m in re.finditer(r'name="[A-Z_]*BACKGROUND[^"]*"\s+value="([0-9A-Fa-f]{6})"', xml):
    assert _relative_luminance("#" + m.group(1)) >= 0.55
```

## macOS Sandboxed App Containers

macOS TCC blocks **all** external process I/O to sandboxed app containers — including
`defaults write`, `PlistBuddy`, `plistlib` file writes, and direct file writes into
`~/Library/Application Support/<App>/`. This is a kernel-level restriction.

**BBEdit 16 is fully sandboxed.** `~/Library/Application Support/BBEdit/Color Schemes/`
cannot be written from install scripts. Do not check `os.path.isdir(bbedit_schemes)`
and write there — it will silently fail.

**Pattern for sandboxed app theme files:**

```python
# Write to non-sandboxed source dir
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "MyTheme.bbColorScheme"), "w") as fh:
    fh.write(scheme_content)

# Tell the user — do NOT write into ~/Library/Application Support/BBEdit/
print(f"BBEdit: open .bbColorScheme files from {out_dir} in BBEdit to install.")
```

**Re-import is required after every regeneration.** Updating the source dir does NOT
automatically update the copy inside BBEdit's sandbox. The user must open the
`.bbColorScheme` file in Finder (or File → Open in BBEdit) each time the theme changes.

## Atuin Theme Files

Custom theme files (`~/.config/atuin/themes/NAME.toml`) must contain a `[theme]`
section with a `name` field in addition to `[colors]`. Without it, the theme silently
fails to load and atuin renders monochrome.

```toml
[theme]
name = "dracula-pro-alucard"   # must match the filename stem

[colors]
Important = "#HEX_COLOR"
```

The `name` must match the filename stem exactly.

## McFly Colors Through SSH+tmux

McFly's `config.toml` only supports the 16 named ANSI colors (e.g., `"grey"`,
`"black"`, `"blue"`). Hex values **silently fall back to white**.

Named ANSI colors render differently depending on the **local terminal emulator's
palette** — the ANSI palette passes through SSH unchanged, but tmux re-renders using
its internal state.

**Ghostty + Dracula Pro Alucard ANSI mapping:**
- ANSI 0 (`black`) = near-white → **washed out as foreground**
- ANSI 7 (`grey`) = near-black → **legible as foreground**
- ANSI 8 (`dark_grey`) = pure white → **washed out**
- ANSI 15 (`white`) = very dark → **legible**

For light mode with Dracula Pro Alucard (Ghostty): `results_fg = "grey"` works;
`results_fg = "black"` or `"dark_grey"` do NOT.

Always test mcfly colors from the specific terminal emulator that will be used — VS
Code and Ghostty can give opposite results for the same config.
