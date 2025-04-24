-- Plugins {{{1
-- =============================================================================

-- nvim-lspconfig {{{2
-- -----------------------------------------------------------------------------

-- https://github.com/neovim/nvim-lspconfig
--
-- Useful commands:
-- :help lsp-quickstart
-- :help lspconfig
-- :help lspconfig-all
-- :checkhealth lsp

-- > vim.lsp.enable('pyright')

-- Can enable debugging with:
-- > vim.lsp.set_log_level("debug")

-- https://github.com/neovim/nvim-lspconfig
vim.lsp.enable('pyright')

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

-- require("mason").setup {}
-- require("mason-lspconfig").setup { ensure_installed = { "pyright", }, }
-- require 'lspconfig'.pyright.setup {}
