"""Tests for Lig's Dracula Pro configuration."""

import os
import runpy
import subprocess
import tomllib
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.parent
_CHEZMOI = _ROOT / "chezmoi"
_TEMPLATE = _CHEZMOI / "dot_config" / "lig" / "config.toml.tmpl"
_INSTALL = runpy.run_path(str(_ROOT / "install"))


def test_lig_palette_uses_named_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    """All popup colors come from the selected palette or terminal default."""
    generate = _INSTALL["_generate_lig_dracula_pro_toml"]
    palette = {
        "bg": "#000000",
        "fg": "#ffffff",
        "selection": "#444444",
        "comment": "#888888",
        "purple": "#aaaaaa",
    }
    monkeypatch.setitem(generate.__globals__, "_parse_vim_palette", lambda *_: palette)
    colors = tomllib.loads(generate("unused", "pro"))["colors"]
    assert colors["bg"] == palette["bg"]
    assert colors["selected_bg"] == palette["selection"]
    assert colors["description_fg"] == palette["comment"]
    assert colors["selected_description_fg"] == palette["fg"]
    assert colors["match_fg"] == palette["purple"]
    assert set(colors.values()) <= {*palette.values(), "default"}
    monkeypatch.setitem(generate.__globals__, "_parse_vim_palette", lambda *_: None)
    assert generate("unused", "pro") is None


@pytest.mark.parametrize(
    ("mode", "filename", "fallback"),
    [
        ("dark", "dracula-pro.toml", "dracula"),
        ("light", "dracula-pro-alucard.toml", "light"),
    ],
)
def test_lig_template_selects_palette_and_falls_back(
    tmp_path: Path, mode: str, filename: str, fallback: str
) -> None:
    """Rendering uses the mode-specific fragment only when Pro is installed."""
    config = tmp_path / "config"
    data = tmp_path / "data"
    palette = config / "koopa" / "lig" / filename
    palette.parent.mkdir(parents=True)
    palette.write_text('[colors]\nbg = "#000000"\n')
    env = {
        **os.environ,
        "XDG_CONFIG_HOME": str(config),
        "XDG_DATA_HOME": str(data),
        "KOOPA_COLOR_MODE": mode,
    }

    def render() -> dict:
        result = subprocess.run(
            ["chezmoi", f"--source={_CHEZMOI}", "execute-template", "--file", str(_TEMPLATE)],
            capture_output=True,
            check=True,
            env=env,
            text=True,
        )
        return tomllib.loads(result.stdout)

    assert render() == {"ui": {"theme": fallback}}
    (data / "dracula-pro").mkdir(parents=True)
    assert render() == {"ui": {"theme": fallback}, "colors": {"bg": "#000000"}}
    palette.unlink()
    assert render() == {"ui": {"theme": fallback}}
