return {
    {
        'nvim-treesitter/nvim-treesitter',
        build = ':TSUpdate',
        event = { 'BufReadPost', 'BufNewFile' },
        config = function()
            require('nvim-treesitter').setup({
                ensure_installed = {
                    'bash', 'c', 'json', 'lua', 'markdown', 'markdown_inline',
                    'python', 'r', 'regex', 'rust', 'toml', 'vim', 'vimdoc', 'yaml',
                },
            })
        end,
    },
    -- Rainbow delimiters (replaces rainbow_parentheses.vim)
    {
        'HiPhish/rainbow-delimiters.nvim',
        event = { 'BufReadPost', 'BufNewFile' },
        submodules = false,
    },
}
