from __future__ import annotations

import re
import sys
from pathlib import Path

from alakazam.config import AlakazamConfig
from alakazam.remote_sync import RemoteSync

# Matches rsync's own remote-shell destination syntax: "[user@]host:path".
# A leading "/" (local absolute path) never matches, since the host part can't contain "/".
REMOTE_SPEC = re.compile(r"^(?:[^/@:]+@)?[^/@:]+:")


def is_remote_spec(drive: str) -> bool:
    return bool(REMOTE_SPEC.match(drive))


def find_mounted_drives(drive_name: list[str]) -> list[str]:
    mounted = [name for name in drive_name if is_remote_spec(name) or Path(name).is_dir()]
    if not mounted:
        raise FileNotFoundError(f"none of the configured drives are mounted: {', '.join(drive_name)}")
    return mounted


def sync(directory: Path, config: AlakazamConfig, *, dry_run: bool) -> None:
    drives = find_mounted_drives(config.drive_name)

    missing = [name for name in config.drive_name if name not in drives]
    for name in missing:
        print(f"warning: drive not mounted, skipping: {name}", file=sys.stderr)

    for drive in drives:
        rsync_options = dict(config.rsync_options)

        if is_remote_spec(drive):
            separator = "" if drive.endswith(":") else "/"
            destination = f"{drive}{separator}{config.drive_path}"
            rsync_options.setdefault("mkpath", True)
        else:
            destination = Path(drive) / config.drive_path
            if not dry_run:
                destination.mkdir(parents=True, exist_ok=True)

        RemoteSync(
            source=directory,
            destination=destination,
            dry_run=dry_run,
            exclude=config.ignore_list,
            **rsync_options,
        ).run()
