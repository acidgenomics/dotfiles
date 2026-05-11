return {
    {
        'saghen/blink.cmp',
        event = 'InsertEnter',
        version = '*',
        opts = {
            enabled = function()
                local disabled = { markdown = true, org = true, text = true }
                return not disabled[vim.bo.filetype]
            end,
            keymap = {
                preset = 'none',
                ['<Tab>'] = { 'show', 'select_next', 'fallback' },
                ['<S-Tab>'] = { 'select_prev', 'fallback' },
                ['<C-y>'] = { 'select_and_accept', 'fallback' },
                ['<C-e>'] = { 'cancel', 'fallback' },
                ['<C-b>'] = { 'scroll_documentation_up', 'fallback' },
                ['<C-f>'] = { 'scroll_documentation_down', 'fallback' },
                ['<C-k>'] = { 'show_signature', 'hide_signature', 'fallback' },
            },
            appearance = {
                nerd_font_variant = 'mono',
            },
            sources = {
                default = { 'lsp', 'path', 'buffer' },
            },
            completion = {
                menu = { auto_show = false },
                documentation = { auto_show = true },
            },
        },
    },
}
