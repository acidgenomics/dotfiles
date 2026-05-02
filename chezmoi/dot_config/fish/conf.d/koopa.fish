# Koopa activation for fish shell.
set -l __koopa_data_home
if set -q XDG_DATA_HOME
    set __koopa_data_home $XDG_DATA_HOME
else
    set __koopa_data_home "$HOME/.local/share"
end
set -l __koopa_activate "$__koopa_data_home/koopa/activate.fish"
if test -r "$__koopa_activate"
    source "$__koopa_activate"
end
