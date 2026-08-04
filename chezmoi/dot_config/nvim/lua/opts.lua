-- Neovim options and mappings.
--
-- Ported from ~/.vimrc (shared with Vim 8) when Neovim stopped sourcing it
-- directly. See init.vim for why: sourcing ~/.vimrc pulled in vim-8-only
-- mappings that intercepted unbracketed-paste bytes and replayed them as
-- editor commands, corrupting pasted text. 'inoremap jk <esc>' is
-- intentionally left out (Insert-mode mappings are the ones a raw paste
-- stream can trigger); 'nnoremap <enter> o<esc>' is ported below since it
-- is Normal-mode only.

-- Leader keys (must be set before lazy.nvim loads plugin specs, since
-- plugin `keys` tables reference '<leader>...').
vim.g.mapleader = ','
vim.g.maplocalleader = '\\'

-- Text formatting
-- ==============================================================================

vim.opt.wrap = true
vim.opt.textwidth = 0
vim.opt.wrapmargin = 0
vim.opt.colorcolumn = '81'
vim.opt.signcolumn = 'yes'

vim.opt.smarttab = true
vim.opt.expandtab = true
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.tabstop = 4

vim.opt.list = true
vim.opt.listchars = { tab = '»·', trail = '·' }

vim.opt.encoding = 'utf-8'
vim.opt.updatetime = 300
vim.opt.backspace = { 'indent', 'eol', 'start' }

-- Navigation
-- ==============================================================================

vim.opt.mouse = 'a'
vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.cursorline = true
vim.opt.showcmd = true
vim.opt.laststatus = 2
vim.opt.ruler = true
vim.opt.wildmenu = true
vim.opt.wildmode = { 'list:longest', 'full' }
vim.opt.number = true

vim.opt.hlsearch = true
vim.opt.ignorecase = true
vim.opt.incsearch = true
vim.opt.showmatch = true
vim.opt.smartcase = true

vim.opt.foldmethod = 'marker'
vim.opt.foldlevelstart = 99
vim.opt.foldenable = false

-- File management
-- ==============================================================================

vim.opt.backup = false

-- Bells
-- ==============================================================================

vim.opt.errorbells = false
vim.opt.visualbell = false

-- Clipboard / pasteboard
-- ==============================================================================

if vim.fn.has('macunix') == 1 then
    vim.opt.clipboard = 'unnamed,unnamedplus'
end

-- Colors
-- ==============================================================================

vim.opt.termguicolors = true

-- Key mappings (bindings)
-- ==============================================================================

-- Split navigation keys:
--
-- - Ctrl+J move to the split below
-- - Ctrl+K move to the split above
-- - Ctrl+L move to the split to the right
-- - Ctrl+H move to the split to the left

vim.keymap.set('n', '<c-j>', '<c-w><c-j>')
vim.keymap.set('n', '<c-k>', '<c-w><c-k>')
vim.keymap.set('n', '<c-l>', '<c-w><c-l>')
vim.keymap.set('n', '<c-h>', '<c-w><c-h>')

-- Enable code fold toggling with the spacebar.
vim.keymap.set('n', '<space>', 'za')

-- Delete line without copying to clipboard, using leader prefix mapping.
-- https://stackoverflow.com/a/11993928/3911732
vim.keymap.set('n', '<leader>d', '"_dd')

-- Add blank line without entering insert mode. Normal mode only (not
-- Insert/Terminal) so it cannot fire mid-paste from a raw/unbracketed
-- paste stream.
vim.keymap.set('n', '<cr>', 'o<esc>')

-- Don't lose selection when shifting sidewards.
vim.keymap.set('x', '<', '<gv')
vim.keymap.set('x', '>', '>gv')

-- Quickly move current line.
vim.keymap.set('n', '[e', ":<c-u>execute 'move -1-'. v:count1<cr>")
vim.keymap.set('n', ']e', ":<c-u>execute 'move +'. v:count1<cr>")

-- Quickly add empty lines.
vim.keymap.set('n', '[<space>', ":<c-u>put! =repeat(nr2char(10), v:count1)<cr>'[")
vim.keymap.set('n', ']<space>', ':<c-u>put =repeat(nr2char(10), v:count1)<cr>')

-- Middle-click paste is a common accidental-paste trigger (stray trackpad
-- click, jitter): neutralize it while keeping the rest of `mouse=a`.
for _, lhs in ipairs({ '<MiddleMouse>', '<2-MiddleMouse>', '<3-MiddleMouse>', '<4-MiddleMouse>' }) do
    vim.keymap.set({ 'n', 'i', 'v' }, lhs, '<Nop>')
end

-- Filetype detection
-- ==============================================================================

-- Detect an R script from its shebang line (Neovim has no builtin rule for
-- this; ported from ~/.vim/ftdetect/r.vim).
vim.api.nvim_create_autocmd({ 'BufNewFile', 'BufRead' }, {
    pattern = '*',
    callback = function(args)
        local line1 = vim.fn.getline(1)
        if line1 == '#!/usr/bin/env Rscript' or line1 == '#!/usr/bin/env R' then
            vim.bo[args.buf].filetype = 'r'
        end
    end,
})
