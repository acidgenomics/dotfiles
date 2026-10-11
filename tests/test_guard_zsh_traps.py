"""Tests for the zsh-trap guard: `guard_zsh_traps.py`.

`ids=$(gh api ...); for id in $ids; do ...` runs its body once with every line
joined, because zsh does not word-split an unquoted parameter. The rule was already
written down, so the hook enforces it. Four more zsh-versus-bash traps follow.

Run with: pytest tests/test_guard_zsh_traps.py
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

_HOOKS_DIR = Path(__file__).parent.parent / "chezmoi" / "dot_agents" / "hooks"
sys.path.insert(0, str(_HOOKS_DIR))
# Keep bytecode out of the chezmoi source tree, which chezmoi would otherwise see.
sys.dont_write_bytecode = True

from guard_zsh_traps import decide

_HOOK_PATH = _HOOKS_DIR / "guard_zsh_traps.py"


@pytest.mark.parametrize(
    "command",
    [
        "ids=$(gh api graphql); for id in $ids; do echo $id; done",
        "ids=$(gh api graphql)\nfor id in $ids\ndo\n  echo $id\ndone",
        "for id in ${ids}; do echo $id; done",
        "for f in a b $files; do echo $f; done",
        "cd /tmp && for x in $list; do echo $x; done",
        "echo hi | (for x in $list; do echo $x; done)",
    ],
)
def test_loop_over_a_bare_scalar_variable_denies(command: str) -> None:
    outcome = decide(command)
    assert outcome is not None
    decision, reason = outcome
    assert decision == "deny"
    assert "while IFS= read -r" in reason


def test_reason_names_the_real_loop_variable_and_source() -> None:
    outcome = decide("for id in $ids; do echo $id; done")
    assert outcome is not None
    reason = outcome[1]
    assert "for id in $ids" in reason
    assert "${(f)ids}" in reason
    assert "${=ids}" in reason


@pytest.mark.parametrize(
    "command",
    [
        # Command substitution IS word-split by zsh.
        "for id in $(gh api graphql); do echo $id; done",
        # Array and positional expansions work per element.
        'for x in "${arr[@]}"; do echo $x; done',
        "for x in ${arr[@]}; do echo $x; done",
        "for x in $@; do echo $x; done",
        # Explicit zsh splitting flags.
        "for x in ${(f)ids}; do echo $x; done",
        "for x in ${=ids}; do echo $x; done",
        # A quoted variable is a single literal word on purpose.
        'for x in "$ids"; do echo $x; done',
        # Literal word lists and globs.
        "for x in a b c; do echo $x; done",
        "for f in *.py; do echo $f; done",
        # Names the same command makes arrays.
        "files=(a b); for f in $files; do echo $f; done",
        "typeset -a files; files+=(a b); for f in $files; do echo $f; done",
        "local -a files; for f in $files; do echo $f; done",
        # The recommended replacement.
        "gh api graphql | while IFS= read -r id; do echo $id; done",
    ],
)
def test_loops_that_work_in_zsh_pass(command: str) -> None:
    assert decide(command) is None


@pytest.mark.parametrize(
    "command",
    [
        # Runs in bash, which splits.
        "bash -c 'for x in $list; do echo $x; done'",
        "sh -c 'for x in $list; do echo $x; done'",
        # A heredoc body is data or another shell's script.
        "cat <<'EOF' | bash\nfor x in $list; do echo $x; done\nEOF",
        "python3 - <<EOF\nprint('for x in $list')\nEOF",
        # Text that merely mentions a loop.
        'grep -n "for x in $list" script.sh',
        "git commit -m 'explain why for x in $list fails'",
    ],
)
def test_text_that_only_mentions_a_loop_passes(command: str) -> None:
    assert decide(command) is None


def test_command_after_a_heredoc_is_still_checked() -> None:
    command = "cat <<EOF\nbody\nEOF\nfor x in $list; do echo $x; done"
    outcome = decide(command)
    assert outcome is not None
    assert outcome[0] == "deny"


def _run_hook(payload: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_HOOK_PATH)],
        input=payload if isinstance(payload, str) else json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )


def test_hook_emits_a_deny_decision_for_the_bad_loop() -> None:
    result = _run_hook({"tool_input": {"command": "for id in $ids; do echo $id; done"}})
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["hookEventName"] == "PreToolUse"
    assert output["permissionDecision"] == "deny"


def test_hook_denies_inside_a_copilot_batched_call() -> None:
    payload = {
        "toolCalls": [
            {"args": {"command": "ls"}},
            {"args": {"command": "for id in $ids; do echo $id; done"}},
        ]
    }
    result = _run_hook(payload)
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "payload",
    [
        "",
        "not json",
        {"tool_input": {"command": None}},
        {"tool_input": "a string"},
        {"tool_input": {}},
    ],
)
def test_hook_fails_open_on_absent_or_malformed_input(payload: object) -> None:
    result = _run_hook(payload)
    assert result.returncode == 0
    assert result.stdout == ""


# ---------------------------------------------------------------------------
# Trap 2: an unquoted word that starts with `=` is a command lookup in zsh.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "echo ======",
        "echo ===== header =====",
        'echo "x"; echo =====',
        '[ "$a" == "b" ] && echo yes',
        "test $a == b",
        "printf '%s\\n' =x",
    ],
)
def test_unquoted_equals_word_denies(command: str) -> None:
    outcome = decide(command)
    assert outcome is not None
    decision, reason = outcome
    assert decision == "deny"
    assert "printf '%s\\n' '------'" in reason


@pytest.mark.parametrize(
    "command",
    [
        "echo '======'",
        'echo "====="',
        "printf '%s\\n' '------'",
        '[[ "$a" == b ]] && echo yes',
        "(( a == b ))",
        "x=$((1==1))",
        '[ "$a" = b ]',
        "tr -d =",
        "awk -F= '{print $1}'",
        "cut -d= -f1",
        "FOO=bar env",
        "echo a=b",
        "echo hi  # ====== a comment",
        "cat <<'EOF'\n=====\nEOF",
        "bash -c 'echo ====='",
    ],
)
def test_equals_that_is_quoted_or_an_operator_passes(command: str) -> None:
    assert decide(command) is None


# ---------------------------------------------------------------------------
# Trap 3: an unquoted glob in an option value is expanded by zsh first.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "grep -rn foo . --include=*.py",
        "grep -rl foo . --exclude-dir=*cache",
        "find . -name *.py",
        "find . -iname *.PY -type f",
        "rg foo -g *.py",
        "rg foo --glob=*.py",
    ],
)
def test_unquoted_glob_option_denies(command: str) -> None:
    outcome = decide(command)
    assert outcome is not None
    decision, reason = outcome
    assert decision == "deny"
    assert "Quote the pattern" in reason


@pytest.mark.parametrize(
    "command",
    [
        "grep -rn foo . '--include=*.py'",
        "grep -rn foo . --include='*.py'",
        'find . -name "*.py"',
        "rg foo -g '*.py'",
        "grep -rn foo . --include=a.py",
        "git ls-files -- '*.py'",
        "echo -name *.py",
        "ls *.py",
    ],
)
def test_quoted_or_plain_globs_pass(command: str) -> None:
    assert decide(command) is None


# ---------------------------------------------------------------------------
# Trap 4: `log` is a zsh builtin that shadows /usr/bin/log.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "log show --last 1h",
        "cd /tmp; log show --last 1h",
        "x=$(log show --last 1m)",
        "if true; then log show --last 1m; fi",
    ],
)
def test_log_as_a_command_denies(command: str) -> None:
    outcome = decide(command)
    assert outcome is not None
    decision, reason = outcome
    assert decision == "deny"
    assert "/usr/bin/log" in reason


@pytest.mark.parametrize(
    "command",
    [
        "/usr/bin/log show --last 1h",
        "git log --oneline",
        "gh run view --log",
        "echo log show",
        "log() { echo hi; }; log hello",
        "log",
    ],
)
def test_log_that_is_not_the_builtin_passes(command: str) -> None:
    assert decide(command) is None


# ---------------------------------------------------------------------------
# Trap 5: `time` inside a command substitution captures nothing.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "out=$( { time sleep 1; } 2>&1 )",
        'out="$(time ls)"',
        "x=`time ls`",
    ],
)
def test_time_inside_a_command_substitution_denies(command: str) -> None:
    outcome = decide(command)
    assert outcome is not None
    decision, reason = outcome
    assert decision == "deny"
    assert "/usr/bin/time" in reason


@pytest.mark.parametrize(
    "command",
    [
        "time sleep 1",
        "/usr/bin/time -p ls",
        "echo $(date +%s)",
        "git log --format=%ct",
    ],
)
def test_time_outside_a_command_substitution_passes(command: str) -> None:
    assert decide(command) is None


def test_hook_emits_a_deny_decision_for_an_unquoted_equals_word() -> None:
    result = _run_hook({"tool_input": {"command": "echo ======"}})
    assert result.returncode == 0
    output = json.loads(result.stdout)["hookSpecificOutput"]
    assert output["permissionDecision"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "echo 'a; for x in $ids; do'",
        'echo "run: for f in $files; do"',
        "git commit -m 'fix for x in $ids; do loop'",
        "for f in $HOME/x/*.sh; do echo $f; done",
        "for f in $dir/*.txt; do echo $f; done",
        "for f in $*; do echo $f; done",
        "for f in $(git -C $L diff --name-only -- src); do echo $f; done",
        "for f in `ls $dir`; do echo $f; done",
        "bash -c 'for x in $ids; do echo $x; done'",
        "bash -lc 'for x in $ids; do echo $x; done'",
        'sh -c "for x in $ids; do echo $x; done"',
        "grep -rn x --include=\\*.py .",
        "echo 'a; time make'; echo $(date)",
        "echo '$(time make)'",
    ],
)
def test_quoted_text_and_non_scalar_words_pass(command: str) -> None:
    assert decide(command) is None, command


@pytest.mark.parametrize(
    "command",
    [
        "bash -c 'echo ok'; for x in $ids; do echo $x; done",
        "sh -c 'true' && echo ====== ",
        "bash -c 'true'; log show --last 1m",
        "for x in ${ids:-a b}; do echo $x; done",
        "for x in $1; do echo $x; done",
        "{ log show --last 1m; }",
        "if log show --last 1m; then echo ok; fi",
        "time log show --last 1m",
        'x="$(cd d; time make)"',
        "echo $(cd d; time make 2>&1)",
        "echo $(ls && time make)",
        'echo "$(for x in $ids; do echo $x; done)"',
    ],
)
def test_traps_outside_a_bash_string_or_in_a_substitution_still_deny(command: str) -> None:
    assert decide(command) is not None, command


def test_glob_reason_shows_the_whole_word() -> None:
    outcome = decide("grep -rn x --include=*.py .")
    assert outcome is not None
    assert "--include=*.py" in outcome[1]
