"""Tests for the Claude Code settings template."""

import json
import subprocess
from pathlib import Path

import pytest

_CHEZMOI = Path(__file__).parent.parent / "chezmoi"


@pytest.mark.parametrize("has_key", [False, True])
def test_api_key_helper(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    has_key: bool,
) -> None:
    """Only enable API-key authentication when a key file exists."""
    home = tmp_path / "home with spaces"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    if has_key:
        claude_dir = home / ".claude"
        claude_dir.mkdir()
        (claude_dir / "api-key").write_text("test-key\n", encoding="utf-8")
    result = subprocess.run(
        [
            "chezmoi",
            f"--source={_CHEZMOI}",
            "execute-template",
            "--file",
            str(_CHEZMOI / "dot_claude" / "settings.json.tmpl"),
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    settings = json.loads(result.stdout)
    if has_key:
        helper = subprocess.run(
            ["sh", "-c", settings["apiKeyHelper"]],
            capture_output=True,
            check=True,
            text=True,
        )
        assert helper.stdout == "test-key\n"
        assert helper.stderr == ""
        (claude_dir / "api-key").unlink()
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.run(
                ["sh", "-c", settings["apiKeyHelper"]],
                capture_output=True,
                check=True,
                text=True,
            )
    else:
        assert "apiKeyHelper" not in settings
    assert "test-key" not in result.stdout
