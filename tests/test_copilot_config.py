"""Tests for the Copilot CLI bridge to `~/.agents`.

Copilot reads user instructions only from `~/.copilot/instructions/*.instructions.md`
and runs hooks only from the JSON files in `~/.copilot/hooks/`. Both are generated from
chezmoi templates, so two things can drift: a rule that has no instruction template
(Copilot never sees it), and a hook entry that names a script which does not exist.

Run with: pytest tests/test_copilot_config.py
"""

import json
from pathlib import Path

import pytest

_CHEZMOI = Path(__file__).parent.parent / "chezmoi"
_RULES = sorted((_CHEZMOI / "dot_agents" / "rules").glob("*.md"))
_HOOKS_DIR = _CHEZMOI / "dot_agents" / "hooks"
_HOOK_TEMPLATE = _CHEZMOI / "private_dot_copilot" / "hooks" / "dotfiles-hooks.json.tmpl"
_KNOWN_EVENTS = {"PreToolUse", "PostToolUse", "SessionStart", "Stop", "UserPromptSubmit"}


@pytest.mark.parametrize("rule", _RULES, ids=lambda p: p.stem)
def test_rule_has_copilot_instruction(rule: Path) -> None:
    """Every rule under dot_agents/rules needs a Copilot instruction template."""
    template = (
        _CHEZMOI / "private_dot_copilot" / "instructions" / f"{rule.stem}.instructions.md.tmpl"
    )
    assert template.is_file(), f"no Copilot instruction template for {rule.name}"
    assert f'"{rule.stem}"' in template.read_text(), (
        f"{template.name} does not name its own rule {rule.stem}"
    )


def test_hook_template_schema_and_scripts() -> None:
    """The public Copilot hook file uses schema version 1 and names real scripts."""
    rendered = _HOOK_TEMPLATE.read_text().replace("{{ .chezmoi.homeDir }}", "/home/test")
    config = json.loads(rendered)
    assert config["version"] == 1
    assert set(config["hooks"]) <= _KNOWN_EVENTS
    scripts = {p.name.removeprefix("executable_") for p in _HOOKS_DIR.iterdir()}
    for groups in config["hooks"].values():
        for group in groups:
            for hook in group["hooks"]:
                script = hook["command"].split("/.agents/hooks/")[1].rstrip('"')
                assert script in scripts, f"hook names missing script {script}"
