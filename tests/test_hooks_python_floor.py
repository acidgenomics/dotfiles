"""Tests for the Python floor of the deployed hooks.

The hooks need Python 3.10 or newer. macOS ships 3.9 as `/usr/bin/python3`, which is
unsupported. Two things hold the line: every hook file must parse as 3.10 code, and
`hook_adapter` must stop with a readable message under an older interpreter instead
of failing with an import-time TypeError.

Run with: pytest tests/test_hooks_python_floor.py
"""

import ast
import subprocess
import sys
from pathlib import Path

import pytest

_HOOKS_DIR = Path(__file__).parent.parent / "chezmoi" / "dot_agents" / "hooks"
_HOOK_FILES = sorted(_HOOKS_DIR.glob("*.py"))


def test_there_are_hook_files_to_check() -> None:
    assert _HOOK_FILES


@pytest.mark.parametrize("path", _HOOK_FILES, ids=lambda p: p.name)
def test_every_hook_parses_as_python_3_10(path: Path) -> None:
    ast.parse(path.read_text(), filename=str(path), feature_version=(3, 10))


@pytest.mark.parametrize("module", ["hook_adapter", "guard_rm", "guard_tmp", "guard_zsh_traps"])
def test_an_older_python_stops_with_a_readable_message(module: str) -> None:
    code = (
        "import sys; sys.dont_write_bytecode = True; sys.version_info = (3, 9, 6); "
        f"sys.path.insert(0, {str(_HOOKS_DIR)!r}); import {module}"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 1
    assert "Python 3.10 or newer" in result.stderr
    assert "TypeError" not in result.stderr
