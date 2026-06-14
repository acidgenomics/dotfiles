# Nushell Environment Config File
#
# version = "0.113.1"

def create_left_prompt [] {
    mut home = ""
    try {
        if $nu.os-info.name == "windows" {
            $home = $env.USERPROFILE
        } else {
            $home = $env.HOME
        }
    }

    let dir = ([
        ($env.PWD | str substring 0..<($home | str length) | str replace $home "~"),
        ($env.PWD | str substring ($home | str length)..)
    ] | str join)

    let path_segment = if (is-admin) {
        $"(ansi red_bold)($dir)"
    } else {
        $"(ansi green_bold)($dir)"
    }

    $path_segment
}

def create_right_prompt [] {
    let time_segment = ([
        (date now | format date '%m/%d/%Y %r')
    ] | str join)

    $time_segment
}

# Use nushell functions to define your right and left prompt
$env.PROMPT_COMMAND = {|| create_left_prompt }
$env.PROMPT_COMMAND_RIGHT = {|| create_right_prompt }

# The prompt indicators are environmental variables that represent
# the state of the prompt
$env.PROMPT_INDICATOR = {|| "> " }
$env.PROMPT_INDICATOR_VI_INSERT = {|| ": " }
$env.PROMPT_INDICATOR_VI_NORMAL = {|| "> " }
$env.PROMPT_MULTILINE_INDICATOR = {|| "::: " }

# Specifies how environment variables are:
# - converted from a string to a value on Nushell startup (from_string)
# - converted from a value back to a string when running external commands (to_string)
# Note: The conversions happen *after* config.nu is loaded
$env.ENV_CONVERSIONS = {
  "PATH": {
    from_string: { |s| $s | split row (char esep) | path expand -n }
    to_string: { |v| $v | path expand -n | str join (char esep) }
  }
  "Path": {
    from_string: { |s| $s | split row (char esep) | path expand -n }
    to_string: { |v| $v | path expand -n | str join (char esep) }
  }
}

# Directories to search for scripts when calling source or use
#
# By default, <nushell-config-dir>/scripts is added
$env.NU_LIB_DIRS = [
    ($nu.config-path | path dirname | path join 'scripts')
]

# Directories to search for plugin binaries when calling register
#
# By default, <nushell-config-dir>/plugins is added
$env.NU_PLUGIN_DIRS = [
    ($nu.config-path | path dirname | path join 'plugins')
]

# To add entries to PATH (on Windows you might use Path), you can use the following pattern:
# $env.PATH = ($env.PATH | split row (char esep) | prepend '/some/path')

# Koopa activation: set KOOPA_PREFIX for activate.nu.
$env.KOOPA_PREFIX = if ($env.XDG_DATA_HOME? | default "" | is-empty) {
    $"($env.HOME)/.local/share/koopa"
} else {
    $"($env.XDG_DATA_HOME)/koopa"
}

# Koopa: ensure cached prompt-tool init exists for parse-time `source` in config.nu.
# Sourcing is deferred to config.nu (nushell evaluates env.nu first, then parses config.nu).
# The mtime-guarded _koopa_activate_starship/_koopa_activate_zoxide in header.nu keep
# the caches fresh on binary upgrade; this block only guarantees they exist on first run.
let _koopa_cache = $"($env.HOME)/.cache/koopa"
for _t in [
    { bin: "starship", args: ["init", "nu"] }
    { bin: "zoxide",   args: ["init", "nushell"] }
] {
    let _out = $"($_koopa_cache)/($_t.bin).nu"
    if not ($_out | path exists) {
        mkdir $_koopa_cache
        let _bin = $"($env.KOOPA_PREFIX)/bin/($_t.bin)"
        if ($_bin | path exists) { ^$_bin ...$_t.args | save -f $_out } else { "" | save -f $_out }
    }
}
