return {
    -- Formatting (replaces ALE formatting for Neovim)
    {
        'stevearc/conform.nvim',
        event = 'BufWritePre',
        cmd = 'ConformInfo',
        opts = {
            formatters_by_ft = {
                python = { 'ruff_format' },
                rust = { 'rustfmt', lsp_format = 'fallback' },
            },
            format_on_save = {
                timeout_ms = 3000,
                lsp_format = 'fallback',
            },
        },
    },
    -- Linting: Python diagnostics come from the ruff language server
    -- (see 'vim.lsp.enable' in init.lua.tmpl), so there is no nvim-lint here.
    -- Running both would report every ruff diagnostic twice.
}
