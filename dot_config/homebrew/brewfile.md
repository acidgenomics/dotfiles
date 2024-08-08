# Homebrew Bundle Brewfile

Updated 2024-08-08.

## Cask reinstallation

Previously installed applications not managed by Homebrew intentionally error
here, and there's no supported method in `brew bundle install` to force an
overwrite. Instead, per app run this command manually:

```sh
brew install --cask --force APP_NAME
```

## See also

- https://github.com/Homebrew/homebrew-bundle/issues/446
