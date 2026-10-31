---
name: dotfiles-ghostty
description: >-
  Troubleshoot Ghostty terminal access on macOS. Use when Ghostty reports
  Permission denied, code 13, or cannot list Documents or OneDrive-backed
  folders, especially when other apps can access the same location.
---

# Ghostty on macOS

## Directory access and privacy permissions

macOS app privacy permissions are distinct from Unix ownership and mode bits.
A shell can enter a directory while a listing command cannot enumerate it.
An error such as the following is a reason to check app privacy permissions,
not proof that the directory needs chmod:

```text
Permission denied: . - code: 13

Skipped 1 directories due to permission denied:
  .
```

### Least-privilege troubleshooting

1. Open **System Settings > Privacy & Security > Files & Folders** and expand
   **Ghostty**.
2. Check the permission matching the storage provider or protected folder.
   For a OneDrive-backed location, enable **OneDrive** under Ghostty. Do not
   assume a path under Documents must have a separate Documents toggle.
   Enable **Documents Folder** instead if that is the relevant entry shown.
3. Retest. If the change has not taken effect, quit Ghostty completely with
   **Command-Q**, reopen it, and retest. Opening another tab is not a full quit.
4. In Ghostty, enter the affected directory and run:

   ```sh
   /bin/ls . >/dev/null && printf 'Directory access works\n'
   l
   ```

   The first command tests directory enumeration without printing filenames.
   If it succeeds but `l` fails, run `type l` to identify the alias, function,
   or executable, then investigate that command rather than broadening access.
5. If access still fails, inspect ownership, ACLs, and flags without modifying
   them, using `/bin/ls -ldeO .` in Ghostty. If narrow privacy permissions are
   unavailable or insufficient, discuss **Full Disk Access** as a broader
   fallback, not the default fix. After enabling it for Ghostty, fully quit
   and reopen the app before testing.

## Gotchas

- Confirmed fix: enabling **OneDrive under Ghostty's Files & Folders entry**
  restored directory listing for a OneDrive-backed folder accessed through
  Documents. Full Disk Access and Unix permission changes were not needed.
- Do not infer that enabling a toggle for the OneDrive app grants Ghostty
  access. The relevant permission is nested under **Ghostty**.
- Desktop or Downloads access does not establish access to another protected
  folder or file provider. Inspect the actual entries shown.
- A direnv loading message alone does not establish that direnv caused the
  failure.
- Do not recommend `sudo`, recursive `chmod`, or recursive `chown` to bypass
  macOS privacy controls. They can alter valid permissions without fixing the
  app's privacy authorization.
- Do not reset privacy permissions with `tccutil` as an initial fix. It changes
  authorization state and requires an explicit, separately justified decision.
- Test in Ghostty itself. Success in another terminal or an editor's agent
  process does not verify Ghostty's app-specific access.
- Do not read or print directory contents merely to diagnose permissions.
