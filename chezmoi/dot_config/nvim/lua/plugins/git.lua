return {
    -- Git signs in the gutter (replaces vim-gitgutter)
    {
        'lewis6991/gitsigns.nvim',
        event = { 'BufReadPost', 'BufNewFile' },
        opts = {
            signs = {
                add = { text = '|' },
                change = { text = '|' },
                delete = { text = '_' },
                topdelete = { text = '‾' },
                changedelete = { text = '~' },
            },
        },
    },
    -- Copilot (Lua native, integrates with blink.cmp)
    {
        'zbirenbaum/copilot.lua',
        cmd = 'Copilot',
        event = 'InsertEnter',
        opts = {
            -- Disabled by default, matching the Vim 8 config.
            suggestion = { enabled = false, auto_trigger = false },
            panel = { enabled = false },
        },
    },
}
