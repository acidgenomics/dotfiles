# Homebrew Bundle Brewfile

Updated 2024-10-28.

## Casks to consider

- audacity
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
- carbon-copy-cloner
- coconutbattery
- coda
- cog
- datagrip
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
- hazel
- iterm2
- julia
- keka
- kitty
- little-snitch
- macvim
- microsoft-openjdk
- museeks
- name-mangler
- neovide
- netnewswire
- nordvpn
- onyx
- oracle-jdk
- osxfuse
- pacifist
- pastebot
- plex-media-server
- positron
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
- superduper
- temurin
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
- xld

## Cask reinstallation

Previously installed applications not managed by Homebrew intentionally error
here, and there's no supported method in `brew bundle install` to force an
overwrite. Instead, per app run this command manually:

```sh
brew install --cask --force APP_NAME
```

## See also

- https://github.com/Homebrew/homebrew-bundle/issues/446
