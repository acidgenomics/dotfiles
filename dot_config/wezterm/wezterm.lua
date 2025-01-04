-- WezTerm configuration
--
-- @note Updated 2025-01-04.
--
-- @seealso
-- * https://wezfurlong.org/wezterm/config/files.html
-- * https://wezfurlong.org/wezterm/config/appearance.html
-- * https://draculatheme.com/wezterm

local wezterm = require "wezterm"
local config = {}

config.color_scheme = "Dracula (Official)"
config.font_size = 16
config.tab_bar_at_bottom = true
config.use_fancy_tab_bar = false
config.window_decorations = "RESIZE"

return config
