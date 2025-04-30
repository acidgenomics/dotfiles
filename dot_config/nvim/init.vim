"""
" Neovim configuration.
" Updated 2025-04-23.
"""

" vim-to-neovim {{{1
" ==============================================================================

" https://neovim.io/doc/user/nvim.html#nvim-from-vim

set runtimepath^=~/.vim runtimepath+=~/.vim/after
let &packpath = &runtimepath
source ~/.vimrc

" init.lua {{{1
" ==============================================================================

lua require('init')
