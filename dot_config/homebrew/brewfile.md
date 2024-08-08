# Homebrew Bundle Brewfile

Updated 2024-08-08.

## Casks to consider

- abbyy-finereader-pdf
- adobe-acrobat-pro
- adobe-creative-cloud
- adobe-dng-converter
- aerial
- airfoil
- anaconda
- audio-hijack
- audirvana
- authy
- bartender
- bettertouchtool
- bluejeans
- boop
- coconutbattery
- coda
- cog
- egnyte
- eloston-chromium
- fiji
- font-open-sans
- font-roboto
- font-roboto-mono
- font-source-code-pro
- font-source-serif-pro
- font-twitter-color-emoji
- gitkraken
- google-cloud-sdk
- handbrake
- julia
- kitty
- macvim
- museeks
- name-mangler
- neovide
- netnewswire
- nordvpn
- onyx
- osxfuse
- pastebot
- plex-media-server
- powershell
- quarto
- r
- rekordbox
- ringcentral
- safari-technology-preview
- scrivener
- skype
- skype-for-business
- sqlworkbenchj
- strawberry
- sublime-text
- textmate
- the-unarchiver
- thonny
- tor-browser
- tower
- vanilla
- virtualbox
- vscodium
- webex
- wine-stable

## Cask reinstallation

Previously installed applications not managed by Homebrew intentionally error
here, and there's no supported method in `brew bundle install` to force an
overwrite. Instead, per app run this command manually:

```sh
brew install --cask --force APP_NAME
```

## See also

- https://github.com/Homebrew/homebrew-bundle/issues/446
