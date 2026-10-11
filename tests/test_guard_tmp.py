"""Tests for the /tmp guard: `guard_tmp.py`.

The guard denies tool calls that would create or write scratch files in /tmp,
/var/tmp, or /dev/shm, and tells the model to use `mktemp` (which honors $TMPDIR).

Two lists drive the file. DENIED must stay blocked (a regression there lets scratch
files back into /tmp). PASSES must reach the normal permission flow (a regression
there brings back false positives on reads, `mktemp`, and $TMPDIR paths).

Run with: pytest tests/test_guard_tmp.py
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

from guard_tmp import decide_bash, decide_file

_GUARD = _HOOKS_DIR / "guard_tmp.py"


@pytest.fixture
def tmpdir_root(tmp_path: Path) -> str:
    """A fake per-user $TMPDIR outside /tmp, plus a symlink inside it that points at /tmp."""
    root = tmp_path / "T"
    root.mkdir()
    (root / "to_tmp").symlink_to("/tmp")
    return str(root.resolve())


DENIED = [
    "cat > /tmp/x <<'EOF'\nhi\nEOF",
    "echo hi >/tmp/x",
    "echo hi > /tmp/x",
    "echo hi >> /tmp/x",
    "echo hi 2>/tmp/err",
    "echo hi &>/tmp/both",
    "ls > /tmp/listing",
    "tee /tmp/x",
    "mktemp -d /tmp/x.XXXX",
    "mktemp /tmp/f.XXXX",
    "mktemp -p /tmp",
    "mktemp --tmpdir=/tmp",
    "mkdir -p /tmp/work",
    "touch /tmp/x",
    "cp a /tmp/b",
    "cp -t /tmp a b",
    "cp --target-directory=/tmp a b",
    "mv a /var/tmp/b",
    "cp a /private/tmp/b",
    "cp a /tmp/../tmp/b",
    "cp a {root}/to_tmp/b",
    "curl -o /tmp/x http://h",
    "wget -O /tmp/x http://h",
    "dd if=a of=/tmp/x",
    "cd /tmp && ls",
    "pushd /tmp",
    "env FOO=1 touch /tmp/x",
    "sudo cp a /tmp/b",
    "bash -c 'echo hi > /tmp/x'",
    "python3 -c \"open('/tmp/x','w').write('a')\"",
    "python3 - <<'EOF'\nimport pathlib\npathlib.Path('/tmp/x').write_text('a')\nEOF",
    "cat /tmp/a > /tmp/b",
    "echo hi > /dev/shm/x",
    "find /tmp -name x -delete",
]

PASSES = [
    "mktemp",
    "mktemp -d",
    "mktemp -t abc",
    'mktemp -d "$TMPDIR/x.XXXX"',
    "cp a $TMPDIR/b",
    "cp /tmp/a b",
    "mv /tmp/a ./a",
    "ls /tmp",
    "ls -la /var/tmp",
    "cat /tmp/x",
    "cat < /tmp/x",
    "python3 job.py < /tmp/in",
    "grep x /tmp/y | wc -l",
    "head -n 5 /tmp/x",
    "rm /tmp/x",
    "rm -r /tmp/x",
    "rmdir /tmp/x",
    "find /tmp -name x",
    'echo "see /tmp/x"',
    "echo /tmp/x",
    "echo hi > {root}/out",
    "cp a {root}/b",
    "mkdir -p {root}/work",
    "cat > {root}/x <<'EOF'\nhi\nEOF",
    "echo hi > out.txt",
    "ls",
    "git status",
    "python3 -c \"print('/tmp is shared')\"",
    "python3 -c \"print(open('/tmp/x').read())\"",
]


@pytest.mark.parametrize("template", DENIED)
def test_denied(template: str, tmpdir_root: str) -> None:
    command = template.replace("{root}", tmpdir_root)
    assert decide_bash(command, tmpdir_root), command


@pytest.mark.parametrize("template", PASSES)
def test_passes(template: str, tmpdir_root: str) -> None:
    command = template.replace("{root}", tmpdir_root)
    assert decide_bash(command, tmpdir_root) is None, command


@pytest.mark.parametrize("path", ["/tmp/x", "/private/tmp/x", "/var/tmp/x", "{root}/to_tmp/x"])
def test_file_tools_are_denied_under_tmp(path: str, tmpdir_root: str) -> None:
    assert decide_file(path.replace("{root}", tmpdir_root), tmpdir_root)


@pytest.mark.parametrize("path", ["{root}/x", "/Users/someone/repo/file.py", "relative.txt", ""])
def test_file_tools_pass_elsewhere(path: str, tmpdir_root: str) -> None:
    assert decide_file(path.replace("{root}", tmpdir_root), tmpdir_root) is None


@pytest.mark.parametrize("inactive", ["", "relative/dir", "/tmp", "/private/tmp", "/var/tmp/x"])
def test_guard_is_inactive_when_tmpdir_is_unset_or_under_tmp(inactive: str) -> None:
    assert decide_bash("echo hi > /tmp/x", inactive) is None
    assert decide_file("/tmp/x", inactive) is None


def test_an_unparsable_command_is_left_to_the_normal_flow(tmpdir_root: str) -> None:
    assert decide_bash("echo 'unterminated > /tmp/x", tmpdir_root) is None


def _hook(payload: dict, tmpdir: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "TMPDIR": tmpdir, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, str(_GUARD)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
    )


def test_hook_blocks_a_bash_write_with_exit_2_and_mentions_mktemp(tmpdir_root: str) -> None:
    result = _hook(
        {"tool_name": "Bash", "tool_input": {"command": "echo hi > /tmp/x"}}, tmpdir_root
    )
    assert result.returncode == 2
    assert "mktemp" in json.loads(result.stderr)["reason"]


def test_hook_blocks_a_write_tool_call(tmpdir_root: str) -> None:
    payload = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/x", "content": "a"}}
    assert _hook(payload, tmpdir_root).returncode == 2


def test_hook_ignores_other_tools(tmpdir_root: str) -> None:
    payload = {"tool_name": "Read", "tool_input": {"file_path": "/tmp/x"}}
    result = _hook(payload, tmpdir_root)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


def test_hook_stays_silent_for_a_clean_command(tmpdir_root: str) -> None:
    payload = {"tool_name": "Bash", "tool_input": {"command": f"echo hi > {tmpdir_root}/x"}}
    result = _hook(payload, tmpdir_root)
    assert (result.returncode, result.stdout, result.stderr) == (0, "", "")


@pytest.mark.parametrize("stdin", ["", "not json", "[]", '{"tool_name": "Bash"}'])
def test_hook_fails_toward_no_decision_on_bad_input(stdin: str, tmpdir_root: str) -> None:
    env = {**os.environ, "TMPDIR": tmpdir_root, "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [sys.executable, str(_GUARD)], input=stdin, capture_output=True, text=True, env=env
    )
    assert (result.returncode, result.stdout) == (0, "")
