-- WezTerm configuration
--
-- @note Updated 2025-01-04.
--
-- @seealso
-- * https://wezfurlong.org/wezterm/config/files.html
-- * https://wezfurlong.org/wezterm/config/appearance.html
-- * https://wezfurlong.org/wezterm/config/lua/
--     wezterm.gui/get_appearance.html
-- * https://draculatheme.com/wezterm

local wezterm = require "wezterm"
local config = {}

config.font_size = 16
config.tab_bar_at_bottom = false
config.use_fancy_tab_bar = false
config.window_decorations = "RESIZE"

-- wezterm.gui is not available to the mux server, so take care to
-- do something reasonable when this config is evaluated by the mux
function get_appearance()
  if wezterm.gui then
    return wezterm.gui.get_appearance()
  end
  return "Dark"
end

function scheme_for_appearance(appearance)
  if appearance:find "Dark" then
    return "Dracula (Official)"
  else
    return "Builtin Solarized Light"
  end
end

config.color_scheme = scheme_for_appearance(get_appearance())

return config
