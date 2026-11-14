"""Tests for the Dracula Pro JetBrains plugin installation."""

import io
import runpy
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import pytest

_INSTALL = runpy.run_path(str(Path(__file__).parent.parent / "install"))


def _plugin_zip(path: Path, *, light: bool = True) -> None:
    jar_data = io.BytesIO()
    with zipfile.ZipFile(jar_data, "w") as jar:
        jar.writestr(
            "META-INF/plugin.xml",
            "<idea-plugin><extensions>"
            '<themeProvider id="new-dark" path="/themes/DraculaPro.theme.json"/>'
            + (
                '<themeProvider id="new-light" path="/themes/DraculaProAlucard.theme.json"/>'
                if light
                else ""
            )
            + "</extensions></idea-plugin>",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr("dracula-pro/lib/dracula-pro-2.1.0.jar", jar_data.getvalue())


@pytest.mark.parametrize(("mode", "active_id"), [("dark", "new-dark"), ("light", "new-light")])
def test_jetbrains_upgrades_plugin_and_uses_vendor_themes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str, active_id: str
) -> None:
    """Replace old plugin files and use both IDs supplied by the new vendor plugin."""
    config = tmp_path / "config"
    data = tmp_path / "data"
    (data / "dracula-pro").mkdir(parents=True)
    bundle = config / "koopa/jetbrains-theme/dracula-pro.zip"
    _plugin_zip(bundle)
    ide = tmp_path / "Library/Application Support/JetBrains/PyCharm2026.1"
    old_lib = ide / "plugins/dracula-pro/lib"
    old_lib.mkdir(parents=True)
    (old_lib / "dracula-pro-1.4.0.jar").write_bytes(b"old")
    (old_lib / "searchableOptions-1.4.0.jar").write_bytes(b"old")
    local_plugin = ide / "plugins/dracula-pro-alucard/lib"
    local_plugin.mkdir(parents=True)
    (local_plugin / "dracula-pro-alucard.jar").write_bytes(b"old")
    configure = _INSTALL["_configure_jetbrains"]
    monkeypatch.setitem(configure.__globals__, "is_macos", lambda: True)
    monkeypatch.setitem(configure.__globals__, "xdg_data_home", lambda: str(data))
    monkeypatch.setitem(configure.__globals__, "xdg_config_home", lambda: str(config))
    monkeypatch.setenv("KOOPA_COLOR_MODE", mode)

    configure(str(tmp_path))

    assert sorted(p.name for p in old_lib.iterdir()) == ["dracula-pro-2.1.0.jar"]
    assert not local_plugin.exists()
    laf = ElementTree.parse(ide / "options/laf.xml")
    assert laf.find(".//laf").get("themeId") == active_id
    assert laf.find(".//preferred-dark-laf").get("themeId") == "new-dark"
    assert laf.find(".//preferred-light-laf").get("themeId") == "new-light"
    assert _INSTALL["_install_jetbrains_plugin"](str(bundle), str(ide / "plugins")) is False


def test_older_plugin_keeps_local_light_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep the generated Alucard fallback when the vendor plugin has no light theme."""
    config = tmp_path / "config"
    data = tmp_path / "data"
    (data / "dracula-pro").mkdir(parents=True)
    _plugin_zip(config / "koopa/jetbrains-theme/dracula-pro.zip", light=False)
    ide = tmp_path / "Library/Application Support/JetBrains/PyCharm2026.1"
    ide.mkdir(parents=True)
    configure = _INSTALL["_configure_jetbrains"]
    monkeypatch.setitem(configure.__globals__, "is_macos", lambda: True)
    monkeypatch.setitem(configure.__globals__, "xdg_data_home", lambda: str(data))
    monkeypatch.setitem(configure.__globals__, "xdg_config_home", lambda: str(config))
    monkeypatch.setitem(
        configure.__globals__, "_generate_pycharm_alucard_theme", lambda _: ("{}", "<scheme/>")
    )
    configure(str(tmp_path))

    assert (ide / "plugins/dracula-pro-alucard/lib/dracula-pro-alucard.jar").is_file()
    laf = ElementTree.parse(ide / "options/laf.xml")
    assert laf.find(".//preferred-dark-laf").get("themeId") == "new-dark"
    assert laf.find(".//preferred-light-laf").get("themeId") == (
        "a71dce76-a3c5-4429-91af-41cf86094740"
    )


def test_invalid_jetbrains_bundle_preserves_installed_plugin(tmp_path: Path) -> None:
    """A malformed bundle must not replace the existing plugin."""
    plugins = tmp_path / "plugins"
    old = plugins / "dracula-pro/lib/old.jar"
    old.parent.mkdir(parents=True)
    old.write_bytes(b"old")
    bundle = tmp_path / "plugin.zip"
    with zipfile.ZipFile(bundle, "w") as zf:
        zf.writestr("../outside", b"invalid")
    with pytest.raises(RuntimeError, match="archive layout"):
        _INSTALL["_install_jetbrains_plugin"](str(bundle), str(plugins))
    assert old.read_bytes() == b"old"
