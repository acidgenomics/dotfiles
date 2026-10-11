#!/usr/bin/env python3
"""PreToolUse hook: keep scratch files out of /tmp. Use `mktemp`, which honors $TMPDIR.

Scratch files in /tmp are shared with every user and process on the machine, they
survive the session, and on macOS they sit outside the per-user $TMPDIR that
`mktemp` uses. This hook denies tool calls that would create or write to /tmp,
/var/tmp, or /dev/shm (including their /private/... spellings and symlinks to
them), and tells the model to run `mktemp -d` and use that path instead.

Denied:

* Write, Edit, MultiEdit, and NotebookEdit whose target path is under those roots.
* Bash that writes there: a redirect (`> /tmp/x`, `2>/tmp/e`, `&>`), `tee`, `touch`,
  `mkdir`, `mktemp` given a /tmp path, `curl -o`, `dd of=`, `cd /tmp`, a `cp`, `mv`,
  `install`, `ln`, or `rsync` whose destination is there, and interpreter code
  (`python3 -c`, a heredoc) that names a /tmp path next to a write.

Not decided (the normal permission flow runs): read-only commands (`ls`, `cat`,
`grep`, ...), a /tmp path used only as a `cp` or `mv` source, and `rm` or `rmdir`,
so legacy files can still be cleaned up with a prompt.

The guard is inactive when $TMPDIR is unset or is itself under one of those roots,
because `mktemp` then produces /tmp paths and a guard would block everything.

Deployed from the public dotfiles tree to `~/.claude/hooks/guard_tmp.py`.
Compatible with Python 3.9, which is what macOS ships as `python3`.
"""

import json
import os
import re
import sys

from shell_command_scan import ParseError, walk

_ROOTS = ("/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp", "/dev/shm")
_DENIED_ROOTS = tuple(sorted(set(_ROOTS) | {os.path.realpath(root) for root in _ROOTS}))
_FILE_TOOLS = frozenset({"Write", "Edit", "MultiEdit", "NotebookEdit"})
_WRAPPERS = frozenset(
    {"sudo", "doas", "env", "command", "nohup", "time", "nice", "exec", "xargs", "busybox"}
)
_READ_ONLY = frozenset(
    {
        "ls", "cat", "head", "tail", "less", "more", "grep", "egrep", "fgrep", "rg", "wc",
        "file", "stat", "du", "diff", "cmp", "readlink", "realpath", "test", "[", "nl", "od",
        "hexdump", "strings", "jq", "md5", "md5sum", "shasum", "sha256sum", "echo", "printf",
        "rm", "rmdir",
    }
)  # fmt: skip
_FIND_WRITES = frozenset({"-delete", "-exec", "-execdir", "-ok", "-fprint", "-fprintf", "-fls"})
_DEST_LAST = frozenset({"cp", "mv", "install", "ln", "rsync", "scp"})
_NAV = frozenset({"cd", "pushd"})
_REDIRECT_BARE = re.compile(r"^(?:\d*|&)(?:>>?|>\|)$")
_REDIRECT_ATTACHED = re.compile(r"^(?:\d*|&)(?:>>?|>\|)(.+)$")
_INPUT_BARE = re.compile(r"^\d*<$")  # `< file`: reads, so it is dropped with its target
_INPUT_ATTACHED = re.compile(r"^\d*<[^<].*$")  # `<file`
_PAYLOAD_PATH = re.compile(
    r"(?<![\w$/.-])(?:/private/var/tmp|/private/tmp|/var/tmp|/tmp|/dev/shm)(?=/|[\"'\s)\]]|$)"
)
_WRITE_MODE = r"[\"'][rwabxt+]*[wax+][rwabxt+]*[\"']"
_WRITE_HINT = re.compile(
    r"open\(\s*[^,()]+,\s*" + _WRITE_MODE
    + r"|mode\s*=\s*" + _WRITE_MODE
    + r"|\.open\(\s*" + _WRITE_MODE
    + r"|write|mkdir|makedirs|mkstemp|Temporary|to_csv|to_parquet|to_json|savefig"
    + r"|\.save\(|dump\(|copy|move|touch|symlink"
)  # fmt: skip

REASON = (
    "Do not use /tmp, /var/tmp, or /dev/shm for scratch files. Run `mktemp -d` (it honors "
    "$TMPDIR), use that path, and delete only what you created."
)


def _tmp_real(raw):
    """Return the real $TMPDIR when the guard should run, else None."""
    if not raw or not os.path.isabs(raw):
        return None
    real = os.path.realpath(raw)
    for root in _DENIED_ROOTS:
        if real == root or real.startswith(root + os.sep):
            return None
    return real


def _is_denied(path, tmp_real):
    """True when an absolute `path` resolves under a denied root and not under $TMPDIR."""
    if not path or "$" in path or "\n" in path or not os.path.isabs(path):
        return False
    real = os.path.realpath(os.path.normpath(path))
    if real == tmp_real or real.startswith(tmp_real + os.sep):
        return False
    return any(real == root or real.startswith(root + os.sep) for root in _DENIED_ROOTS)


def _split_redirects(argv):
    """Return (words without redirects, write-redirect targets)."""
    words = []
    targets = []
    expect_target = False
    skip_input = False
    for word in argv:
        if skip_input:
            skip_input = False
        elif expect_target:
            targets.append(word)
            expect_target = False
        elif _REDIRECT_BARE.match(word):
            expect_target = True
        elif _INPUT_BARE.match(word):
            skip_input = True
        elif _INPUT_ATTACHED.match(word):
            continue
        else:
            match = _REDIRECT_ATTACHED.match(word)
            if match and not match.group(1).startswith("&"):
                targets.append(match.group(1))
            elif not match:
                words.append(word)
    return words, targets


def _command_index(words):
    """Index of the command word, looking past wrappers and their options."""
    i = 0
    while i < len(words):
        if os.path.basename(words[i]) in _WRAPPERS:
            i += 1
            while i < len(words) and (
                words[i].startswith("-") or ("=" in words[i] and not words[i].startswith("/"))
            ):
                i += 1
            continue
        return i
    return None


def _destinations(args):
    """The words a cp/mv/install/ln/rsync/scp call writes to."""
    plain = []
    target = None
    expect = False
    for word in args:
        if expect:
            target, expect = word, False
        elif word in ("-t", "--target-directory"):
            expect = True
        elif word.startswith("--target-directory="):
            target = word.split("=", 1)[1]
        elif not (word.startswith("-") and word != "-"):
            plain.append(word)
    return [target] if target is not None else plain[-1:]


def _values(word):
    """A word, plus the value of a `key=value` word such as `of=/tmp/x`."""
    return [word, word.split("=", 1)[1]] if "=" in word and not word.startswith("/") else [word]


def _check_invocation(inv, tmp_real):
    words, targets = _split_redirects(inv.argv)
    if any(_is_denied(t, tmp_real) for t in targets):
        return REASON
    for payload in inv.payloads:
        if _PAYLOAD_PATH.search(payload) and _WRITE_HINT.search(payload):
            return REASON
    i = _command_index(words)
    if i is None:
        return None
    name = os.path.basename(words[i])
    args = words[i + 1 :]
    if name in _DEST_LAST:
        candidates = _destinations(args)
    elif name == "find":
        if not _FIND_WRITES.intersection(args):
            return None
        candidates = args
    elif name in _READ_ONLY:
        return None
    else:
        candidates = args
    if name not in _NAV and name not in _DEST_LAST and name != "find":
        candidates = [value for word in candidates for value in _values(word)]
    return REASON if any(_is_denied(c, tmp_real) for c in candidates) else None


def decide_bash(command, tmpdir=""):
    """Return the deny reason for a Bash command, or None."""
    tmp_real = _tmp_real(tmpdir)
    if tmp_real is None:
        return None
    try:
        invocations = walk(command)
    except ParseError:
        return None
    for inv in invocations:
        reason = _check_invocation(inv, tmp_real)
        if reason:
            return reason
    return None


def decide_file(path, tmpdir=""):
    """Return the deny reason for a file-tool target path, or None."""
    tmp_real = _tmp_real(tmpdir)
    if tmp_real is None:
        return None
    return REASON if _is_denied(path, tmp_real) else None


def main():
    """Read the hook payload from stdin; exit 2 with a reason to deny. Fail toward no decision."""
    try:
        payload = json.load(sys.stdin)
        tool = payload.get("tool_name", "")
        tool_input = payload["tool_input"]
        tmpdir = os.environ.get("TMPDIR", "")
        if tool in _FILE_TOOLS:
            path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
            reason = decide_file(path, tmpdir)
        elif tool == "Bash":
            command = tool_input.get("command")
            reason = decide_bash(command, tmpdir) if isinstance(command, str) else None
        else:
            reason = None
    except Exception:
        return 0
    if reason:
        print(json.dumps({"decision": "block", "reason": reason}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
