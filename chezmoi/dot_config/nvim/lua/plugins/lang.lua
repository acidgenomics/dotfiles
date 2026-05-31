return {
    -- R support (Lua rewrite of Nvim-R by the same author)
    {
        'R-nvim/R.nvim',
        ft = { 'r', 'rmd', 'quarto', 'rnoweb', 'rhelp' },
        cond = function()
            return vim.fn.executable('R') == 1
        end,
        config = function()
            require('r').setup({
                R_app = 'radian',
                R_args = {},
                R_cmd = 'R',
                bracketed_paste = true,
                min_editor_width = 80,
                rconsole_width = 80,
                rconsole_height = 20,
            })
        end,
    },
    -- Quarto
    {
        'quarto-dev/quarto-nvim',
        ft = 'quarto',
        dependencies = {
            'jmbuhr/otter.nvim',
            'nvim-treesitter/nvim-treesitter',
        },
        opts = {},
    },
    -- Rust (full rust-analyzer integration)
    {
        'mrcjkb/rustaceanvim',
        ft = 'rust',
        version = '^5',
    },
    -- Markdown
    {
        'preservim/vim-markdown',
        ft = 'markdown',
        dependencies = { 'godlygeek/tabular' },
        init = function()
            vim.g.vim_markdown_folding_level = 2
            -- Disable annoying list indentation handling.
            -- https://github.com/preservim/vim-markdown/issues/126
            vim.api.nvim_create_autocmd({ 'BufNewFile', 'BufRead' }, {
                pattern = '*.md',
                callback = function()
                    vim.cmd('filetype plugin indent off')
                end,
            })
        end,
    },
    -- Pandoc
    {
        'vim-pandoc/vim-pandoc',
        ft = { 'pandoc', 'markdown', 'rmd' },
        dependencies = {
            'vim-pandoc/vim-pandoc-syntax',
            'vim-pandoc/vim-markdownfootnotes',
            'vim-pandoc/vim-rmarkdown',
        },
        init = function()
            vim.g['pandoc#filetypes#pandoc_markdown'] = 0
            vim.g['pandoc#syntax#conceal#blacklist'] = { 'strikeout', 'list', 'quotes' }
        end,
    },
}
