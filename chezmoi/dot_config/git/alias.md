# Alias dictionary

- `aa`: Add all unstaged changes.
- `br`: Show more information about current branches.
- `ca`: Commit all unstaged changes, interactively.
- `catchup`: Catch up from main upstream branch.
- `cleanup`: Clean up the repo. Don't mask `clean` with an alias!
- `cm`: Commit with a message, non-interactively.
- `contrib`: List contributors, ordered by the number of commits.
- `dev`: Checkout develop branch.
- `find`: Find commits by source code.
- `find-msg`: Find commits by commit message.
- `glog`: Show custom text-based graphical log of the commit history.
  See also:
  - https://git-scm.com/docs/git-log
  Currently there's not an easy way to reverse graph mode natively.
  - https://zwischenzugs.com/2016/06/04/power-git-log-graphing/
  Inspired by these examples:
  - https://levelup.gitconnected.com/use-git-like-a-senior-engineer-ef6d741c898e
  - https://gist.github.com/simonsmith/6779382
- `ignored`: Show ignored files.
  Credit: https://stackoverflow.com/a/4855096
- `last`: Show the last commit.
- `ll`: Show custom log of the commit history.
- `lrb`: List remote branches. Defaults to `origin`.
- `main`: Check out `main` branch.
- `retag`: Remove the tag with the specified tag name if exists and tag the
  latest commit with that name.
- `tracked`: Show only tracked files.
  Credit: https://stackoverflow.com/a/15606995
- `u`: Update the content of the last commit by including all staged changes.
  The term "update" is used here loosely. Git doesn't actually update the last
  commit, but instead, creates a new commit based on the last commit and
  replaces it.
- `ua`: Update the content of the last commit by including all local changes.
- `um`: Update the content of the last commit, including all staged changes, and
  allow the user to change the commit message.
- `undo`: Undo commits. By default, only reverts the last commit.
- `untracked`: Show untracked files.
  Credit: https://stackoverflow.com/a/4855096
- `web`: Start web-based visualizer. If you hit a Ruby error, run
  `gem install webrick` to resolve.
