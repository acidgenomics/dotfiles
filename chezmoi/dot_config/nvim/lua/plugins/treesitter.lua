return {
    {
        'nvim-treesitter/nvim-treesitter',
        build = ':TSInstall bash c json lua markdown markdown_inline python r regex rnoweb rust toml vim vimdoc yaml',
        event = { 'BufReadPost', 'BufNewFile' },
    },
    -- Rainbow delimiters (replaces rainbow_parentheses.vim)
    {
        'HiPhish/rainbow-delimiters.nvim',
        event = { 'BufReadPost', 'BufNewFile' },
        submodules = false,
    },
}
