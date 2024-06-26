#!/usr/bin/env bash

set -Eeuo pipefail

main() {
    local tic
    tic='/usr/bin/tic'
    [[ -x "$tic" ]] || return 1
    prefix="${PWD:?}"
    "$tic" -x -o "$prefix" 'terminfo-24bit-colon.src'
    "$tic" -x -o "$prefix" 'terminfo-24bit-semicolon.src'
    return 0
}

main "$@"
