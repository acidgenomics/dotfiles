"""PreToolUse hook: deny Bash commands that hit a known zsh-versus-bash trap.

This host's Bash tool is zsh. Five traps have each failed a session here after
the rule was already written down, so this hook makes the rule mechanical:
reading the command is the fix, not remembering the rule.

1. `for x in $var`: zsh does not word-split an unquoted *parameter* expansion, so
   `ids=$(gh api ...); for id in $ids; do ...; done` runs the body ONCE with every
   line joined into one `$id` (2026-10-10, 2026-10-11). bash splits it.
2. An unquoted word that starts with `=`: zsh runs a command lookup on it, so
   `echo ======` fails with `===== not found`, and so does `[ "$a" == "b" ]`.
3. An unquoted glob in an option value (`grep --include=*.py`, `find -name *.py`,
   `rg -g *.py`): zsh fails with `no matches found` when nothing matches, and
   silently swaps in file names when something does.
4. `log` as a command: it is a zsh builtin that shadows `/usr/bin/log`.
5. `time` inside `$( ... )` or backticks: it is a reserved word, so its report goes
   to the shell's stderr and `2>&1` captures nothing.

Every check skips heredoc bodies and the string after `bash -c` / `sh -c` (those
run in bash; the rest of the command is still checked), and reads only unquoted
text. Checks 1 and 5 do read a `$( ... )` or backtick body inside double quotes,
because zsh runs it. Checks 2 and 3 also skip `[[ ... ]]` and `(( ... ))`, where
`==` is an operator.

Trap 1 denies only a word that is a bare scalar in the `for` list: `$name`,
`${name}`, `${name:-default}`, or `$1`. A word with more text (`$HOME/x/*.sh`) is
globbed after expansion, so it works. These also pass, because they work in zsh:

- `for x in $(cmd)`: an unquoted command substitution IS word-split.
- `for x in "${arr[@]}"` and `for x in $@`: array and positional expansions.
- `for x in ${(f)var}` and `${=var}`: the explicit zsh splitting flags.
- `for x in $name` when the same command assigns `name=(...)`, `name+=(...)`,
  or declares it with `typeset -a` / `declare -a` / `local -a`: an array.
- A loop inside a heredoc body or a `bash -c` / `sh -c` string: those run in
  bash, which splits.
- A quoted mention of a loop, such as `echo 'for x in $v; do'`.

The decision is `deny`, not `ask`: an `ask` has no one to answer it in an
unattended session. The reason carries the working replacement.

Also guards against a crash on absent/malformed stdin, like the other
Bash-matcher hooks: `load_payload` returns None instead of raising, and
`read_commands` never raises.

Deployed from the public dotfiles tree to `~/.agents/hooks/guard_zsh_traps.py`.
Needs `hook_adapter.py` beside it, and Python 3.10 or newer (the adapter's
annotations use `X | None`).
"""

import json
import re
import sys

from hook_adapter import load_payload, read_commands

# `for NAME in WORDS` at the start of a statement, WORDS ending at `;`, a
# newline, or the `do` keyword. Anchoring on the statement start keeps text
# that merely mentions a loop (a quoted grep pattern, a commit message) out.
_FOR_RE = re.compile(
    r"(?:^|[;&|({]|\bthen\b|\bdo\b)\s*for\s+\w+\s+in\s+(?P<words>[^;\n]*?)\s*(?:;|\n|$|\bdo\b)",
    re.MULTILINE,
)
_HEREDOC_RE = re.compile(r"<<-?\s*(?P<q>['\"]?)(?P<tag>\w+)(?P=q)")
_BASH_STRING_RE = re.compile(
    r"\b(?:ba)?sh\s+(?:-\w+\s+)*?-\w*c\s+(?P<s>\"(?:[^\"\\]|\\.)*\"|'[^']*')"
)
_SUBSTITUTION_RE = re.compile(r"\$\([^()]*(?:\([^()]*\)[^()]*)*\)|`[^`]*`")
_QUOTED_RE = re.compile(r"\"[^\"]*\"|'[^']*'")
# A word that is exactly a scalar expansion: `$name`, `${name}`, `${name:-default}`,
# or `$1`. `$(`, `$@`, `$*`, `${name[@]}`, `${(f)name}`, and `$HOME/x` do not match.
_SCALAR_RE = re.compile(
    r"^\$(?:(?P<plain>[A-Za-z_]\w*)|\{(?P<braced>[A-Za-z_]\w*)(?::?[-=+?][^}]*)?\}|(?P<digit>[1-9]))$"
)

# One word of a `for` list. A `${...}`, `$( ... )`, or backtick group is one word, even
# when it holds spaces or other variables.
_WORD_RE = re.compile(r"\$\([^()]*(?:\([^()]*\)[^()]*)*\)|\$\{[^}]*\}|`[^`]*`|\S+")
_COMMENT_RE = re.compile(r"(?m)(?:^|(?<=\s))#.*$")
# `[[ ... ]]` and `(( ... ))` (also `$(( ... ))`): `==` and `*` are operators there.
_TEST_RE = re.compile(r"\[\[.*?\]\]|\(\(.*?\)\)", re.DOTALL)
_GLOB_CHAR = r"(?<!\\)[*?\[]"  # an escaped `\*` is a literal star
_OPTION_GLOB_RE = re.compile(
    r"--(?:include|exclude|exclude-dir|include-dir|glob|iglob)=\S*" + _GLOB_CHAR
)
_FIND_GLOB_RE = re.compile(
    r"(?:^|\s)-(?:i?name|i?path|i?wholename|i?regex)\s+[^\s;&|]*" + _GLOB_CHAR
)
_RG_GLOB_RE = re.compile(r"(?:^|\s)(?:-g|--glob|--iglob)\s+[^\s;&|]*" + _GLOB_CHAR)
_FIND_CMD_RE = re.compile(r"\bfind\b")
_RG_CMD_RE = re.compile(r"\b(?:rg|fd)\b")
_COMMAND_START = r"(?:^|[;&|({!]|\bthen\b|\bdo\b|\bif\b|\bwhile\b|\buntil\b|\btime\b)"
_LOG_RE = re.compile(_COMMAND_START + r"\s*log\s+\S", re.MULTILINE)
_LOG_DEFINED_RE = re.compile(r"\blog\s*\(\s*\)|\bfunction\s+log\b|\balias\s+log=")
_TIME_RE = re.compile(r"(?:^|[;&|({!]|\bthen\b|\bdo\b)\s*time\s", re.MULTILINE)

_REASON = (
    "zsh does not word-split an unquoted variable, so `for {var} in ${name}` runs the "
    "body once with every line joined. Pipe the source into a reader instead: "
    "`cmd | while IFS= read -r {var}; do ...; done`. To keep the list in a variable, "
    "split it explicitly: `for {var} in ${{(f){name}}}` (newline) or `${{={name}}}` (spaces)."
)
_EQUALS_REASON = (
    "zsh runs a command lookup on an unquoted word that starts with `=`, so `echo ======` "
    "fails with `===== not found`, and so does `[ a == b ]`. Quote the word, print a "
    "separator with `printf '%s\\n' '------'`, or compare with `=` or `[[ ... ]]`."
)
_GLOB_REASON = (
    "zsh expands the unquoted glob in `{word}` before the command runs: it fails with "
    "`no matches found` when no file matches and swaps in file names when one does. "
    "Quote the pattern, for example `'--include=*.py'` or `-name '*.py'`."
)
_LOG_REASON = (
    "`log` is a zsh builtin that shadows `/usr/bin/log`, so `log show ...` fails with "
    "`too many arguments`. Call `/usr/bin/log` explicitly."
)
_TIME_REASON = (
    "`time` is a zsh reserved word, so inside `$( ... )` its report goes to the shell's "
    "stderr and `2>&1` captures nothing. Measure with `/usr/bin/time` or epoch timestamps."
)


def _strip_heredoc_bodies(command: str) -> str:
    """Drop heredoc bodies, whose lines are data or another shell's script."""
    kept: list[str] = []
    terminator: str | None = None
    for line in command.splitlines():
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        kept.append(line)
        match = _HEREDOC_RE.search(line)
        if match:
            terminator = match.group("tag")
    return "\n".join(kept)


def _mask_quotes(text: str) -> str:
    """Blank out quoted strings but keep their length, so positions stay put.

    A double-quoted string keeps its `$( ... )` and backtick bodies, because
    zsh runs them.
    """

    def _mask(match: re.Match) -> str:
        quoted = match.group(0)
        if quoted[0] == "'":
            return " " * len(quoted)
        chars = [" "] * len(quoted)
        for inner in _SUBSTITUTION_RE.finditer(quoted):
            chars[inner.start() : inner.end()] = quoted[inner.start() : inner.end()]
        return "".join(chars)

    return _QUOTED_RE.sub(_mask, text)


def _substitution_bodies(text: str) -> list[str]:
    """Return the text inside every `$( ... )` and backtick pair in *text*."""
    bodies: list[str] = []
    for match in re.finditer(r"\$\(", text):
        depth, end = 1, match.end()
        while end < len(text) and depth:
            depth += {"(": 1, ")": -1}.get(text[end], 0)
            end += 1
        bodies.append(text[match.end() : end - 1 if depth == 0 else end])
    bodies.extend(re.findall(r"`([^`]*)`", text))
    return bodies


def _array_names(command: str) -> set[str]:
    """Names the command itself makes arrays, which zsh expands per element."""
    names = set(re.findall(r"\b(\w+)\+?=\(", command))
    for decl in re.finditer(r"\b(?:typeset|declare|local)\s+-\w*a\w*\s+(\w+)", command):
        names.add(decl.group(1))
    return names


def _unquoted_text(scanned: str) -> str:
    """Return *scanned* without quoted strings, comments, `[[ ]]`, and `(( ))`."""
    text = _QUOTED_RE.sub("", scanned)
    text = _COMMENT_RE.sub("", text)
    return _TEST_RE.sub(" ", text)


def _for_loop_reason(masked: str, _text: str) -> str | None:
    """Trap 1: `for x in $var` over an unquoted scalar variable."""
    arrays = _array_names(masked)
    for loop in _FOR_RE.finditer(masked):
        for word in _WORD_RE.findall(loop.group("words")):
            var = _SCALAR_RE.match(word)
            if var is None:
                continue
            name = var.group("plain") or var.group("braced") or var.group("digit")
            if name in arrays:
                continue
            loop_var = re.search(r"for\s+(\w+)\s+in", loop.group(0))
            return _REASON.format(var=loop_var.group(1) if loop_var else "x", name=name)
    return None


def _equals_word_reason(_scanned: str, text: str) -> str | None:
    """Trap 2: an unquoted word of two or more characters that starts with `=`."""
    for word in re.split(r"[\s;&|()<>]+", text):
        if len(word) > 1 and word.startswith("="):
            return _EQUALS_REASON
    return None


def _glob_reason(_scanned: str, text: str) -> str | None:
    """Trap 3: an unquoted glob in an option value that zsh expands first."""
    patterns = [_OPTION_GLOB_RE]
    if _FIND_CMD_RE.search(text):
        patterns.append(_FIND_GLOB_RE)
    if _RG_CMD_RE.search(text):
        patterns.append(_RG_GLOB_RE)
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            end = match.end()
            while end < len(text) and not text[end].isspace():
                end += 1  # show the whole word, not only the part up to the glob
            return _GLOB_REASON.format(word=text[match.start() : end].strip())
    return None


def _log_reason(_scanned: str, text: str) -> str | None:
    """Trap 4: `log` as a command, unless the command defines its own `log`."""
    if _LOG_DEFINED_RE.search(text):
        return None
    return _LOG_REASON if _LOG_RE.search(text) else None


def _time_reason(masked: str, _text: str) -> str | None:
    """Trap 5: the `time` keyword at a command position inside a command substitution."""
    if any(_TIME_RE.search(body) for body in _substitution_bodies(masked)):
        return _TIME_REASON
    return None


_CHECKS = (_for_loop_reason, _equals_word_reason, _glob_reason, _log_reason, _time_reason)


def decide(command: str) -> tuple[str, str] | None:
    """Return (permission decision, reason), or None to defer to the normal flow.

    Parameters
    ----------
    command : str
        The full shell command the Bash tool is about to run.

    Returns
    -------
    tuple[str, str] | None
        ``("deny", reason)`` for the first zsh trap the command hits, otherwise
        None. The string after ``bash -c`` / ``sh -c`` is skipped, because bash runs
        it; the rest of the command is still checked.
    """
    command = _BASH_STRING_RE.sub(lambda m: m.group(0)[: m.start("s") - m.start()] + "''", command)
    scanned = _strip_heredoc_bodies(command)
    masked = _mask_quotes(scanned)
    text = _unquoted_text(scanned)
    for check in _CHECKS:
        reason = check(masked, text)
        if reason is not None:
            return ("deny", reason)
    return None


def main() -> None:
    """Read the PreToolUse payload from stdin and emit a deny decision if needed."""
    payload = load_payload(sys.stdin.read())
    if payload is None:
        return
    for command in read_commands(payload):
        outcome = decide(command)
        if outcome is not None:
            decision, reason = outcome
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": decision,
                            "permissionDecisionReason": reason,
                        }
                    }
                )
            )
            return


if __name__ == "__main__":
    main()
