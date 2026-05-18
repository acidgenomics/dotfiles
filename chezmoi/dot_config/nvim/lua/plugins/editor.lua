return {
    -- Fuzzy finder
    {
        'nvim-telescope/telescope.nvim',
        cmd = 'Telescope',
        keys = {
            { '<leader>ff', '<cmd>Telescope find_files<cr>', desc = 'Find Files' },
            { '<leader>fg', '<cmd>Telescope live_grep<cr>', desc = 'Live Grep' },
            { '<leader>fb', '<cmd>Telescope buffers<cr>', desc = 'Buffers' },
            { '<leader>fh', '<cmd>Telescope help_tags<cr>', desc = 'Help Tags' },
        },
        dependencies = {
            'nvim-lua/plenary.nvim',
            { 'nvim-telescope/telescope-fzf-native.nvim', build = 'make' },
        },
        config = function()
            local telescope = require('telescope')
            telescope.setup({})
            telescope.load_extension('fzf')
        end,
    },
    -- File explorer (edit filesystem like a buffer)
    {
        'stevearc/oil.nvim',
        cmd = 'Oil',
        keys = {
            { '-', '<cmd>Oil<cr>', desc = 'Open parent directory' },
        },
        dependencies = { 'nvim-tree/nvim-web-devicons' },
        opts = {},
    },
    -- Sidebar file tree
    {
        'nvim-neo-tree/neo-tree.nvim',
        branch = 'v3.x',
        cmd = 'Neotree',
        keys = {
            { '<leader>e', '<cmd>Neotree toggle<cr>', desc = 'Toggle file tree' },
        },
        dependencies = {
            'nvim-lua/plenary.nvim',
            'nvim-tree/nvim-web-devicons',
            'MunifTanjim/nui.nvim',
        },
        opts = {
            filesystem = {
                filtered_items = {
                    visible = true,
                    hide_dotfiles = false,
                    hide_gitignored = false,
                },
                follow_current_file = { enabled = true },
            },
            window = {
                position = 'left',
                width = 35,
            },
        },
    },
    -- Surround (Lua rewrite of tpope/vim-surround)
    {
        'kylechui/nvim-surround',
        event = 'VeryLazy',
        opts = {},
    },
    -- Git integration
    {
        'tpope/vim-fugitive',
        cmd = { 'Git', 'G', 'Gdiffsplit', 'Gread', 'Gwrite', 'GMove', 'GDelete', 'GBrowse' },
    },
    -- Zoxide integration
    {
        'nanotee/zoxide.vim',
        cmd = { 'Z', 'Zi', 'Zt', 'Zti' },
    },
}
