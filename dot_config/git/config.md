# Global git configuration

## Conditional configuration

See also:

- https://www.brantonboehm.com/code/conditional-git-config/
- https://blog.scottlowe.org/2023/12/15/conditional-git-configuration/
- https://news.ycombinator.com/item?id=38942892
- https://stackoverflow.com/questions/74012449/
- https://stackoverflow.com/questions/2114111/

## Private credentials

Do not store sensitive information, such as the Git user credentials ("email",
"name", "signingkey"), in this file. Add them in a separate 'config-private'
file instead. This is sourced automatically at the bottom of our configuration
here.

Can check current configuration with:

```sh
git config --list --show-origin --show-scope
git config --get user-email
```

## [core]

How to resolve issues with UTF-8 on macOS:

- https://opensource.apple.com/source/Git/Git-48/src/git/compat/precompose_utf8.c.auto.html
- https://stackoverflow.com/questions/5581857/

## [credential]

Particularly useful for commits over HTTPS, on machines where we don't have SSH
keys configured for GitHub.

```sh
git config --global credential.helper 'cache --timeout=10000000'
```

Alternatively, can use `osxkeychain` on macOS to store PAT tokens in keychain.

Can disable Git Credential Manager for Windows prompts with:

```sh
modalPrompt = false
```

### Repo-specific PAT configuration

Enabling `usehttppath` allows for usage of multiple PAT on a single machine,
which can be useful for updating work and personal repos side-by-side. However,
this will trigger PAT prompt for each repo, which can be a tad annoying.

See also:

- https://git-scm.com/docs/git-credential-store
- https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage
- https://happygitwithr.com/credential-caching.html
- https://stackoverflow.com/a/5343146/3911732

## [include]

Includes should remain at the end of the config file in order to allow any of
the default configs to be overwritten by personal or work-specific ones.

See also:

- https://git-scm.com/docs/git-config#_includes

## [difftool]

Useful global environment variables:

- `DFT_BACKGROUND`: dark, light.
- `DFT_DISPLAY`: side-by-side, side-by-side-show-both, inline.

See also:

- https://difftastic.wilfred.me.uk/git.html

## [pretty]

Pretty formats.

See also:

- https://git-scm.com/docs/pretty-formats

## [pull]

Default behavior changed in git 2.27.0:

```
warning: Pulling without specifying how to reconcile divergent branches is
discouraged. You can squelch this message by running one of the following
commands sometime before your next pull:

    git config pull.rebase false  # merge (the default strategy)
    git config pull.rebase true   # rebase
    git config pull.ff only       # fast-forward only

You can replace "git config" with "git config --global" to set a default
preference for all repositories. You can also pass --rebase, --no-rebase, or
--ff-only on the command line to override the configured default per invocation.
```

## References

- https://github.com/alrra/dotfiles/blob/main/src/git/gitconfig
- https://github.com/roryk/dotfiles/blob/master/gitconfig
- https://github.com/vsbuffalo/dotfiles/blob/master/.gitconfig
