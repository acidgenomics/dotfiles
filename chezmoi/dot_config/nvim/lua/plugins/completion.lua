return {
    {
        'saghen/blink.cmp',
        event = 'InsertEnter',
        version = '*',
        opts = {
            keymap = { preset = 'default' },
            appearance = {
                nerd_font_variant = 'mono',
            },
            sources = {
                default = { 'lsp', 'path', 'buffer' },
            },
            completion = {
                documentation = { auto_show = true },
            },
        },
    },
}
