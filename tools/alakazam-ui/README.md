# alakazam-ui

A macOS menu bar app for monitoring and triggering `alakazam` syncs.

```
uv run alakazam-ui
```

Each registered folder shows up as a row in the menu bar dropdown:

```
my-notes   🟢
photos     🟡
archive    🔴
secrets    🟣
```

- 🟢 in sync — a dry-run rsync diff against the drive reports no changes.
- 🟡 out of sync — the drive is mounted, but rsync would transfer something.
- 🔴 drive not attached — none of the folder's configured local drives are mounted.
- 🟣 SSH-only — every configured drive is a remote (`host:path`) spec; these aren't checked.
- ⏳ checking — a check or sync is currently running for that folder.
- ⚠️ error — rsync or config loading failed; see the folder's `alakazam.toml`.

**Click a row** to run a real sync for that folder immediately.

**+ Add New Config** opens a folder picker. The chosen folder must already contain an
`alakazam.toml` (see the sibling `alakazam` project for its format).

**Manage Configs** lets you remove a previously-added folder from the list.

Status is rechecked automatically whenever a volume is mounted or unmounted, and on a slow
periodic fallback timer, in case a folder's contents changed without a drive event.

## Data

Registered folders are stored in `~/.alakazam-config` as JSON:

```json
{
  "entries": [
    {"folder_path": "/Users/me/notes", "last_status": "in_sync", "last_checked_at": "2026-01-01T12:00:00"}
  ]
}
```

## Packaging as an app

```
task install-app   # builds dist/Alakazam.app and copies it to /Applications
task build-app      # just builds dist/Alakazam.app, no install
```

To regenerate the icon from a different source image:

```
sips -z 1024 1024 your-image.png --out /tmp/alakazam.iconset/icon_1024x1024.png
# ...repeat for 16/32/64/128/256/512, plus the @2x variants...
iconutil -c icns /tmp/alakazam.iconset -o resources/alakazam.icns
```
