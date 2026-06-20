# Apache-2.0 License File Conventions (Acid Genomics)

Applies to all repos under `~/git/personal/` and `~/.local/share/koopa/`.

## How GitHub detects licenses

GitHub uses the Ruby `licensee` gem. It normalizes the LICENSE file body
(strips markdown, collapses whitespace) and computes similarity against SPDX
canonical texts. Detection requires ≥98% match — any abridged or altered text
drops below the threshold and the repo shows `NOASSERTION` in the sidebar.

**Content is what matters, not filename.** `LICENSE`, `LICENSE.md`, `LICENSE.txt`
are all recognized equally. Format (plain text vs markdown) is stripped during
matching.

Verify detection status:
```sh
gh api repos/acidgenomics/<repo> --jq '.license.spdx_id'
# Apache-2.0 = detected; NOASSERTION = not detected
```

## Canonical sources by repo type

### Python packages + koopa + dotfiles → `LICENSE` (plain text)

Source: GitHub's own reference copy, guaranteed to match licensee exactly.

```sh
gh api /licenses/apache-2.0 --jq '.body' > LICENSE
```

Verify after writing:
```sh
grep -c 'consequential' LICENSE   # must be 1 (corrupted copies say "exemplary")
```

### R packages → `LICENSE.md` (markdown-formatted)

Source: the usethis bundled template, which is the CRAN-expected format.

```sh
cp "$(Rscript -e 'cat(system.file("templates/license-apache-2.md", package="usethis"))')" LICENSE.md
```

Or locate it directly:
```
/Library/Frameworks/R.framework/Versions/4.6/Resources/site-library/usethis/templates/license-apache-2.md
```

`LICENSE.md` must appear in `.Rbuildignore` (CRAN prohibits bundling standard
license text in the package tarball):
```
^LICENSE\.md$
```

`DESCRIPTION` field: `License: Apache License (>= 2)`

Verify:
```sh
grep -c 'consequential' LICENSE.md   # must be 1
grep 'LICENSE' .Rbuildignore         # must show ^LICENSE\.md$
```

## The corruption that triggered this audit

All plaintext `LICENSE` files across koopa, dotfiles, and all `py-*` packages
once shared an abridged variant (MD5 `7216c64b041f0b8284981ca10dddaf1c`, 193
lines, 10805 bytes). Key missing/altered content vs canonical:

- §8 "Limitation of Liability": said **"exemplary damages"**, canonical says
  **"consequential damages"** — the single fastest check.
- §1 "Contribution" definition: truncated (dropped "any work of authorship,
  including the original version of the Work…").
- §1 "Derivative Works" definition: dropped "whether in Source or Object form".
- Several §4 redistribution clauses were abridged.

The R `LICENSE.md` files used the markdown-reflowed usethis format, which has
canonical text. So R packages were detected (`Apache-2.0`) while everything
else was not (`NOASSERTION`). Fixed 2026-06-20 by replacing all files with
their respective canonical sources above.

## Scope of repos affected

| Repos | File | Source |
|---|---|---|
| `koopa`, `dotfiles` | `LICENSE` | `gh api /licenses/apache-2.0` |
| `py-acidbase`, `py-acidgenomes`, `py-acidplyr`, `py-cellosaurus`, `py-goalie`, `py-pipette`, `py-syntactic` | `LICENSE` | `gh api /licenses/apache-2.0` |
| all 24 `r-*` | `LICENSE.md` | usethis template |

R packages do NOT have a plain `LICENSE` file — `LICENSE.md` + `.Rbuildignore`
entry is the complete, correct setup.

## Adding a license badge (README)

Dynamic badge — renders "Apache-2.0" once detection is working:
```md
![License: Apache-2.0](https://img.shields.io/github/license/acidgenomics/<repo>)
```

koopa and dotfiles READMEs have this badge on the line after the lifecycle badge
(added 2026-06-20). Python package READMEs do not currently carry a badge.
