# Dracula Pro Alucard theme for Kakoune
# https://draculatheme.com/kakoune
#
# Color palette derived from Dracula Pro Alucard (light variant).
# https://draculatheme.com/pro

# Color palette ────────────────────────────────────────────────────────────────

# Standard
declare-option str background 'fafafa'
declare-option str foreground '383a42'
declare-option str selection 'e8e8e8'
declare-option str comment 'a0a1a7'
declare-option str red 'e45649'
declare-option str orange '986801'
declare-option str yellow '986801'
declare-option str green '50a14f'
declare-option str purple 'a626a4'
declare-option str cyan '147172'
declare-option str pink 'e45649'

# ANSI
declare-option str black 'e8e8e8'
declare-option str red 'e45649'
declare-option str green '50a14f'
declare-option str yellow '986801'
declare-option str blue 'a626a4'
declare-option str magenta 'e45649'
declare-option str cyan '147172'
declare-option str white '383a42'
declare-option str bright_black 'a0a1a7'
declare-option str bright_red 'C41860'
declare-option str bright_green '1A8A0D'
declare-option str bright_yellow 'A38A1C'
declare-option str bright_blue '7D5EF5'
declare-option str bright_magenta 'C41860'
declare-option str bright_cyan '1A8A8B'
declare-option str bright_white '000000'

# Alpha blending
declare-option str cursor_alpha '99'
declare-option str selection_alpha '80'

# UI variants
declare-option str background_lighter 'E8E8F0'
declare-option str background_light 'EBEBF5'
declare-option str background_dark 'DEDEE8'
declare-option str background_darker 'e8e8e8'

# Other
declare-option str non_text "%opt{background_light}"

# Template ─────────────────────────────────────────────────────────────────────

# For code
set-face global value "rgb:%opt{purple}"
set-face global type "rgb:%opt{pink}"
set-face global variable "rgb:%opt{cyan}"
set-face global module "rgb:%opt{yellow}"
set-face global function "rgb:%opt{green}"
set-face global string "rgb:%opt{yellow}"
set-face global keyword "rgb:%opt{pink}"
set-face global operator "rgb:%opt{pink}"
set-face global attribute "rgb:%opt{pink}"
set-face global comment "rgb:%opt{comment}"
set-face global documentation comment
set-face global meta "rgb:%opt{pink}"
set-face global builtin "rgb:%opt{cyan}+i"

# Diffs
set-face global DiffText "rgb:%opt{comment}"
set-face global DiffHeader "rgb:%opt{comment}"
set-face global DiffInserted "rgb:%opt{green},rgba:%opt{green}20"
set-face global DiffDeleted "rgb:%opt{red},rgba:%opt{red}50"
set-face global DiffChanged "rgb:%opt{orange}"

# For markup
set-face global title "rgb:%opt{purple}+b"
set-face global header "rgb:%opt{purple}+b"
set-face global mono "rgb:%opt{green}"
set-face global block "rgb:%opt{orange}"
set-face global link "rgb:%opt{cyan}"
set-face global bullet "rgb:%opt{cyan}"
set-face global list "rgb:%opt{foreground}"

# Builtin faces
set-face global Default "rgb:%opt{foreground},rgb:%opt{background}"
set-face global PrimarySelection "default,rgba:%opt{pink}%opt{selection_alpha}"
set-face global SecondarySelection "default,rgba:%opt{purple}%opt{selection_alpha}"
set-face global PrimaryCursor "default,rgba:%opt{pink}%opt{cursor_alpha}"
set-face global SecondaryCursor "default,rgba:%opt{purple}%opt{cursor_alpha}"
set-face global PrimaryCursorEol "rgb:%opt{background},rgb:%opt{foreground}+fg"
set-face global SecondaryCursorEol "rgb:%opt{background},rgb:%opt{foreground}+fg"
set-face global MenuForeground "rgb:%opt{foreground},rgb:%opt{selection}"
set-face global MenuBackground "rgb:%opt{foreground},rgb:%opt{background_dark}"
set-face global MenuInfo "rgb:%opt{comment}"
set-face global Information Default
set-face global Error "rgb:%opt{foreground},rgb:%opt{red}"
set-face global DiagnosticError "rgb:%opt{red}"
set-face global DiagnosticWarning "rgb:%opt{cyan}"
set-face global StatusLine "rgb:%opt{foreground},rgb:%opt{background_dark}"
set-face global StatusLineMode "rgb:%opt{green}"
set-face global StatusLineInfo "rgb:%opt{purple}"
set-face global StatusLineValue "rgb:%opt{green}"
set-face global StatusCursor "rgb:%opt{background},rgb:%opt{foreground}"
set-face global Prompt StatusLine
set-face global BufferPadding "rgb:%opt{non_text}"

# Builtin highlighter faces
set-face global LineNumbers "rgb:%opt{non_text}"
set-face global LineNumberCursor "rgb:%opt{foreground}"
set-face global LineNumbersWrapped "rgb:%opt{background}"
set-face global MatchingChar "rgb:%opt{green}+uf"
set-face global Whitespace "rgb:%opt{non_text}+f"
set-face global WrapMarker "rgb:%opt{non_text}"
