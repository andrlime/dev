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
```

- `drive_name`: mount points to sync to. Every one that's currently mounted gets synced; any that aren't mounted are skipped with a warning (it's an error only if none are mounted).
- `drive_path`: subpath on each drive to sync the directory into.
- `ignore_list`: rsync `--exclude` patterns, in addition to the defaults (`.venv`, `.claude`, `.DS_Store`, `__pycache__`).
