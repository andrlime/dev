# alakazam

Sync a directory to one or more external drives via rsync, configured per-directory.

```
alakazam sync /some/directory [--dry-run] [--config-filename alakazam.toml]
```

Reads `/some/directory/alakazam.toml` (override the filename with `--config-filename`):

```toml
ignore_list = ["some", "paths", "to", "ignore"]
drive_path = "path/on/drive"
drive_name = ["/Volumes/name_of_drive", "/Volumes/name_of_other_drive"]

[rsync]
delete = true
checksum = true
```

- `drive_name`: mount points to sync to, or remote rsync destinations in `[user@]host:path` form (e.g. `"banana:backups"`), synced over SSH. Local mount points that aren't currently mounted are skipped with a warning; remote specs are always attempted. It's an error only if no destination is usable.
- `drive_path`: subpath on each drive to sync the directory into.
- `ignore_list`: rsync `--exclude` patterns, in addition to the defaults (`.venv`, `.claude`, `.DS_Store`, `__pycache__`).
- `rsync`: optional table overriding any `RemoteSync` field (see `alakazam/remote_sync.py`) by name, e.g. `delete`, `checksum`, `bwlimit`. Omitted fields use `RemoteSync`'s own default. `source`, `destination`, `dry_run`, and `exclude` are set by alakazam itself and can't be overridden here.
