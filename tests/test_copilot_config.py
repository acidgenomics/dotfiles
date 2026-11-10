"""Tests for the shared global agent instructions."""

import subprocess
from pathlib import Path

import pytest

_CHEZMOI = Path(__file__).parent.parent / "chezmoi"


@pytest.mark.parametrize("template", ["dot_codex/AGENTS.md.tmpl", "dot_gemini/GEMINI.md.tmpl"])
def test_global_agent_instructions_render(template: str) -> None:
    """Codex and Gemini instructions render the shared base without removed rules."""
    result = subprocess.run(
        [
            "chezmoi",
            f"--source={_CHEZMOI}",
            "execute-template",
            "--file",
            str(_CHEZMOI / template),
        ],
        capture_output=True,
        check=True,
        text=True,
    )
    assert (_CHEZMOI / "dot_claude" / "CLAUDE.md").read_text().strip() in result.stdout
