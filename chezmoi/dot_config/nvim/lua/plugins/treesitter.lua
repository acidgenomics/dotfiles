return {
    {
        -- The 'main' branch rewrite: it does not support lazy-loading, it
        -- compiles parsers with the 'tree-sitter' CLI, and it does not start
        -- highlighting by itself.
        'nvim-treesitter/nvim-treesitter',
        lazy = false,
        build = ':TSUpdate',
        config = function()
            local parsers = {
                'bash', 'c', 'json', 'lua', 'markdown', 'markdown_inline',
                'python', 'r', 'regex', 'rnoweb', 'rust', 'toml', 'vim',
                'vimdoc', 'yaml',
            }
            -- Installing parsers needs the 'tree-sitter' CLI. Without it, skip
            -- the install so nvim still starts (run 'koopa install tree-sitter').
            if vim.fn.executable('tree-sitter') == 1 then
                require('nvim-treesitter').install(parsers)
            end
            -- Start highlighting where a parser exists; pcall ignores the
            -- filetypes that have none.
            vim.api.nvim_create_autocmd('FileType', {
                callback = function(args)
                    pcall(vim.treesitter.start, args.buf)
                end,
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
