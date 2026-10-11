"""Tests for the Copilot CLI bridge to `~/.agents`.

Copilot reads user instructions only from `~/.copilot/instructions/*.instructions.md`
and runs hooks only from the JSON files in `~/.copilot/hooks/`. Both are generated from
chezmoi templates, so two things can drift: a rule that has no instruction template
(Copilot never sees it), and a hook entry that names a script which does not exist.

Run with: pytest tests/test_copilot_config.py
"""

from pathlib import Path

import pytest

_CHEZMOI = Path(__file__).parent.parent / "chezmoi"
_RULES = sorted((_CHEZMOI / "dot_agents" / "rules").glob("*.md"))


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
