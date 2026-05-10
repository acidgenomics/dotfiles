return {
    {
        'nvim-treesitter/nvim-treesitter',
        build = ':TSUpdate',
        event = { 'BufReadPost', 'BufNewFile' },
        opts = {
            ensure_installed = {
                'bash', 'c', 'json', 'lua', 'markdown', 'markdown_inline',
                'python', 'r', 'regex', 'rust', 'toml', 'vim', 'vimdoc', 'yaml',
            },
            highlight = { enable = true },
            indent = { enable = true },
        },
        config = function(_, opts)
            require('nvim-treesitter.configs').setup(opts)
        end,
    },
    -- Rainbow delimiters (replaces rainbow_parentheses.vim)
    {
        'HiPhish/rainbow-delimiters.nvim',
        event = { 'BufReadPost', 'BufNewFile' },
    },
}
