# Lessons

> Cross-project patterns. Managed in chezmoi — edit the source, not ~/.claude directly.
> Per-project lessons go in .claude/rules/lessons.md within the repo.

## Plan Files: System-Generated Names Must Be Used As-Is

When the system specifies a plan filename (in the plan mode system message), use that exact path — do NOT rename it with a `YYYY-MM-DD-` prefix. VS Code's plan review UI looks for the exact filename the system specified; renaming breaks the UI.

The `YYYY-MM-DD-` date prefix convention applies only to manually created plan/reference docs, not system-assigned plan filenames.

## JSON Formatting

- Always use 2-space indentation for JSON files. Never use 4 spaces.
- This applies to all JSON: config files, `.claude/settings.json`, package.json,
  tsconfig, etc.
- When writing or reformatting JSON, use `json.dumps(obj, indent=2)` or
  `JSON.stringify(obj, null, 2)`.

## Deep Research Should Always Include GitHub Code Search

When running deep-research workflows on technical/protocol questions, always include a second parallel workflow specifically targeting GitHub code and repository implementations. The canonical workflow is two parallel runs:
1. Web/protocol research (standards docs, blog posts, issue trackers)
2. GitHub code search (real implementations, usage patterns, adoption evidence)

GitHub code search routinely surfaces implementation details (exact escape sequences, version numbers, adoption tables) that are absent from web sources. This pattern found the definitive mode 2031 solution that was missed by web search alone.

## Never Use `/tmp` for Sensitive Files

`/tmp` is world-readable on many systems and trivially scraped. Never write sensitive content (plaintext secrets, key material, decrypted configs) there.

Always use `mktemp` without a path argument — it respects `$TMPDIR`, which on macOS resolves to a per-user private directory under `/var/folders/` with mode `700`.

```sh
# correct
tmpfile=$(mktemp)

# never
tmpfile=/tmp/myfile
```

In Python, use `tempfile.NamedTemporaryFile` or `tempfile.mkstemp()` — both respect `tempfile.gettempdir()` which honours `$TMPDIR`.

Always `rm` or close+delete the temp file immediately after use.

## Removing Sensitive Files from Git History: Use git filter-repo

When sensitive files need to be purged from git history, use `git filter-repo`
— not delete-and-recreate. Deleting the repo loses settings, branch protections,
access controls, and issue/PR history. `git filter-repo` achieves the same
sanitization with no collateral damage.

```sh
git filter-repo \
    --path path/to/sensitive-file \
    --invert-paths \
    --force
```

`git filter-repo` removes the remote as a safety measure — re-add it after:

```sh
git remote add origin <url>
git push --force --set-upstream origin main
```

Teammates must then re-clone or hard reset:

```sh
git fetch --all && git reset --hard origin/main
```

**Known issue**: `git filter-repo` crashes if any git config value contains a
literal newline (e.g. a multi-line alias). Workaround:

```sh
GIT_CONFIG_NOSYSTEM=1 HOME=/dev/null git filter-repo --path ... --invert-paths --force
```

## Rewriting Commit Identity History: Use git filter-repo --mailmap

When commits carry wrong author/committer emails (e.g. corporate email leaked
into a personal OSS repo), use `git filter-repo --mailmap` — the simplest and
correct tool for pure identity rewrites:

```sh
# mailmap format: canonical <right@email.com> <wrong@email.com>
cat > mailmap << 'EOF'
USER NAME <USER EMAIL> <wrong.name@corp.com>
EOF

GIT_CONFIG_NOSYSTEM=1 HOME=/dev/null git filter-repo --mailmap mailmap --force
git remote add origin <url>   # filter-repo removes the remote as a safety measure
git config --local user.name  "USER NAME"
git config --local user.email "USER EMAIL"
```

**Choose this vs `git commit-tree` replay based on whether commits are unique:**

- Offending commits have **distinct trees** (real unique work) → use `--mailmap`.
  Filter-repo preserves graph topology and rewrites identity metadata only.
- Offending commits are **duplicates** of clean-identity commits (e.g. history
  was doubled by a botched cleanup + git pull re-merge) → use a `git commit-tree`
  replay to de-duplicate. Filter-repo cannot collapse duplicate lineages.

**How to check before choosing:**
```sh
# For each bad email, count distinct trees — if each is unique, mailmap is safe
git log --all --format='%T %ae' | grep 'corp\.com' | awk '{print $1}' | sort -u | wc -l
# Must equal the commit count; if less, duplicates exist and commit-tree is needed
```

**Verification after mailmap rewrite** (must all pass before force-push):
```sh
# 1. No bad identities remain (must print nothing):
git log --all --format='%ae%n%ce' | grep -iE 'corp\.com'

# 2. Good bots preserved (count should be unchanged):
git log --all --format='%ce' | grep -c 'noreply@github\.com'

# 3. Commit count unchanged:
git rev-list --all --count
```

Always bundle-backup first (`git bundle create backup.bundle --all`) and keep it
until the force-push is confirmed correct on the remote.
