local koopa_color_mode = vim.env.KOOPA_COLOR_MODE or ''
local is_light = koopa_color_mode == 'light'
local dracula_pro = vim.fn.expand('~/.vim/pack/theme/start/dracula_pro')
local has_dracula_pro = vim.fn.isdirectory(dracula_pro) == 1
local dracula_pro_variant = vim.env.KOOPA_DRACULA_PRO_VARIANT or 'pro'
local dracula_pro_scheme = dracula_pro_variant == 'pro'
    and 'dracula_pro'
    or ('dracula_pro_' .. dracula_pro_variant:gsub('-', '_'))

-- Build a lualine theme from the live Dracula Pro palette.
-- Dracula Pro ships airline/lightline themes but no lualine theme, so lualine's
-- 'auto' theme guesses from highlight groups and produces washed-out grays.
-- Each variant colorscheme (pro, alucard, van_helsing, ...) overwrites this global,
-- so reading it after :colorscheme yields the active variant. No hex is hardcoded.
local function dracula_pro_lualine_theme()
    local p = vim.g['dracula_pro#palette']
    if type(p) ~= 'table' or type(p.purple) ~= 'table' then
        return nil
    end
    local function c(name)
        return p[name] and p[name][1] or nil
    end
    local outer = { bg = c('selection'), fg = c('fg') }
    local inner = { bg = c('bgdark'), fg = c('fg') }
    local function mode(accent)
        return {
            a = { bg = c(accent), fg = c('bg'), gui = 'bold' },
            b = outer,
            c = inner,
        }
    end
    local muted = { bg = c('bgdark'), fg = c('comment') }
    return {
        normal = mode('purple'),
        insert = mode('green'),
        visual = mode('yellow'),
        replace = mode('red'),
        command = mode('cyan'),
        terminal = mode('green'),
        inactive = {
            a = vim.tbl_extend('force', muted, { gui = 'bold' }),
            b = muted,
            c = muted,
        },
    }
end

return {
    -- Dark colorscheme (dracula.nvim unless dracula_pro is installed locally)
    {
        'Mofiqul/dracula.nvim',
        lazy = false,
        priority = 1000,
        cond = not is_light and not has_dracula_pro,
        config = function()
            vim.cmd.colorscheme('dracula')
        end,
    },
    -- Dracula Pro (loaded from local directory, handles dark + light)
    {
        'dracula_pro',
        dir = dracula_pro,
        lazy = false,
        priority = 1000,
        cond = has_dracula_pro,
        config = function()
            if is_light then
                vim.cmd.colorscheme('dracula_pro_alucard')
            else
                vim.cmd.colorscheme(dracula_pro_scheme)
            end
        end,
    },
    -- Light colorscheme fallback (vim-one when Dracula Pro not installed)
    {
        'rakr/vim-one',
        lazy = false,
        priority = 1000,
        cond = is_light and not has_dracula_pro,
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
                local ok = pcall(vim.cmd.colorscheme, dracula_pro_scheme)
                if not ok then
                    ok = pcall(vim.cmd.colorscheme, 'dracula')
                end
                if not ok then
                    vim.cmd.colorscheme('habamax')
                end
            end,
            set_light_mode = function()
                vim.o.background = 'light'
                local ok = has_dracula_pro
                    and pcall(vim.cmd.colorscheme, 'dracula_pro_alucard')
                    or false
                if not ok then
                    ok = pcall(vim.cmd.colorscheme, 'one')
                end
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
        opts = function()
            return {
                options = {
                    -- Function form: re-evaluated on every ColorScheme event, so a
                    -- dark<->light flip re-derives from the new palette.
                    theme = function()
                        return dracula_pro_lualine_theme() or 'auto'
                    end,
                    component_separators = { left = '', right = '' },
                    section_separators = { left = '', right = '' },
                },
                sections = {
                    lualine_a = { 'mode' },
                    lualine_b = { 'branch', 'diff' },
                    lualine_c = { { 'filename', path = 1 } },
                    lualine_x = { 'diagnostics', 'filetype' },
                    lualine_y = { 'progress' },
                    lualine_z = { 'location' },
                },
            }
        end,
    },
}
