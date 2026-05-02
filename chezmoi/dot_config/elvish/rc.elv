# Koopa activation for Elvish.
use path

var data-home = (or (get-env XDG_DATA_HOME) (path:join (get-env HOME) '.local' 'share'))
var koopa-prefix = (path:join $data-home 'koopa')
var koopa-activate = (path:join $koopa-prefix 'activate.elv')

if (path:is-regular $koopa-activate) {
    set-env KOOPA_PREFIX $koopa-prefix
    eval (slurp < $koopa-activate)
}
