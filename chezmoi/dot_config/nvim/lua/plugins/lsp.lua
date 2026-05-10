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
    -- Linting (replaces ALE linting for Neovim)
    {
        'mfussenegger/nvim-lint',
        event = { 'BufReadPost', 'BufWritePost' },
        config = function()
            local lint = require('lint')
            lint.linters_by_ft = {
                python = { 'ruff' },
            }
            vim.api.nvim_create_autocmd({ 'BufWritePost', 'BufReadPost' }, {
                callback = function()
                    lint.try_lint()
                end,
            })
        end,
    },
}
