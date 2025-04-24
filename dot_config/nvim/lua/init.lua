--[[
nvim-lspconfig

* https://github.com/neovim/nvim-lspconfig

Useful commands:
:help lsp-quickstart
:help lspconfig
:help lspconfig-all
:checkhealth lsp

Can enable debugging with:
> vim.lsp.set_log_level("debug")
]]

--[[
mason-lspconfig (alternate configuration)

* https://github.com/williamboman/mason-lspconfig.nvim
* https://github.com/neovim/nvim-lspconfig/blob/master/doc/configs.md

:help mason-lspconfig.nvim
:help mason-lspconfig-introduction
:help mason-lspconfig-quickstart
:help mason-lspconfig-settings

> require("mason").setup()
> require("mason-lspconfig").setup()

After setting up mason-lspconfig you may set up servers via lspconfig
> require("lspconfig").lua_ls.setup {}
> require("lspconfig").rust_analyzer.setup {}
> ...

> require("mason-lspconfig").setup {
>     ensure_installed = { "pyright", "r_language_server" },
> }
]]

-- Bash
vim.lsp.enable('bashls')

-- Python
-- > vim.lsp.enable('pyright')
vim.lsp.enable('ruff')

-- R
vim.lsp.enable('r_language_server')

-- Air (for R)
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

require("lspconfig").r_language_server.setup({
    on_attach = function(client, _)
        client.server_capabilities.documentFormattingProvider = false
        client.server_capabilities.documentRangeFormattingProvider = false
    end,
})

