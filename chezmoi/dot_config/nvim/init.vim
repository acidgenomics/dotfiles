"""
" Neovim configuration.
" Updated 2026-08-04.
"""

" init.lua {{{1
" ==============================================================================

" Neovim configuration lives entirely in Lua (see lua/init.lua and
" lua/opts.lua). It no longer sources ~/.vimrc / ~/.vim, which used to bridge
" vim-8-only mappings (e.g. 'inoremap jk <esc>', 'nnoremap <enter> o<esc>')
" into Neovim. Those mappings intercepted bytes from unbracketed pastes and
" replayed them as editor commands, producing duplicated/corrupted pasted
" text. ~/.vimrc remains the config for Vim 8.

lua require('init')
