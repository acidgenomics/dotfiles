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

" Plugins {{{1
" ==============================================================================

" nvim-lspconfig {{{2
" ------------------------------------------------------------------------------

" https://github.com/neovim/nvim-lspconfig
"
" Useful commands:
" :help lsp-quickstart
" :help lspconfig
" :help lspconfig-all
" :checkhealth lsp

vim.lsp.enable('pyright')

" Can enable debugging with:
" > vim.lsp.set_log_level("debug")

lua << EOF
-- https://posit-dev.github.io/air/editor-neovim.html
require("lspconfig").air.setup({
    on_attach = function(_, bufnr)
        vim.api.nvim_create_autocmd("BufWritePre", {
            buffer = bufnr,
            callback = function()
                vim.lsp.buf.format()
            end,
        })
    end,
})
EOF
