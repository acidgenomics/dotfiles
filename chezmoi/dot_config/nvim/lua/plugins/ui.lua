local koopa_color_mode = vim.env.KOOPA_COLOR_MODE or ''
local is_light = koopa_color_mode == 'light'
local dracula_pro = vim.fn.expand('~/.vim/pack/theme/start/dracula_pro')

return {
    -- Dark colorscheme (dracula.nvim unless dracula_pro is installed locally)
    {
        'Mofiqul/dracula.nvim',
        lazy = false,
        priority = 1000,
        cond = not is_light and not vim.fn.isdirectory(dracula_pro),
        config = function()
            vim.cmd.colorscheme('dracula')
        end,
    },
    -- Light colorscheme
    {
        'rakr/vim-one',
        lazy = false,
        priority = 1000,
        cond = is_light,
        config = function()
            vim.cmd.colorscheme('one')
        end,
    },
    -- Auto dark/light mode on macOS
    {
        'f-person/auto-dark-mode.nvim',
        lazy = false,
        cond = vim.fn.has('macunix') == 1,
        opts = {
            update_interval = 1000,
            set_dark_mode = function()
                vim.o.background = 'dark'
                local ok = pcall(vim.cmd.colorscheme, 'dracula')
                if not ok then
                    vim.cmd.colorscheme('habamax')
                end
            end,
            set_light_mode = function()
                vim.o.background = 'light'
                local ok = pcall(vim.cmd.colorscheme, 'one')
                if not ok then
                    vim.cmd.colorscheme('habamax')
                end
            end,
        },
    },
    -- Statusline
    {
        'nvim-lualine/lualine.nvim',
        event = 'VeryLazy',
        dependencies = { 'nvim-tree/nvim-web-devicons' },
        opts = {
            options = {
                theme = 'auto',
                component_separators = { left = '', right = '' },
                section_separators = { left = '', right = '' },
            },
        },
    },
}
