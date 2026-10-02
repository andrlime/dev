from __future__ import annotations

import sys
from pathlib import Path

from alakazam.config import AlakazamConfig
from alakazam.remote_sync import RemoteSync


def find_mounted_drives(drive_name: list[str]) -> list[Path]:
    mounted = [Path(candidate) for candidate in drive_name if Path(candidate).is_dir()]
    if not mounted:
        raise FileNotFoundError(f"none of the configured drives are mounted: {', '.join(drive_name)}")
    return mounted


def sync(directory: Path, config: AlakazamConfig, *, dry_run: bool) -> None:
    drives = find_mounted_drives(config.drive_name)

    missing = [name for name in config.drive_name if Path(name) not in drives]
    for name in missing:
        print(f"warning: drive not mounted, skipping: {name}", file=sys.stderr)

    for drive in drives:
        destination = drive / config.drive_path
        if not dry_run:
            destination.mkdir(parents=True, exist_ok=True)

        RemoteSync(
            source=directory,
            destination=destination,
            delete=True,
            dry_run=dry_run,
            exclude=config.ignore_list,
        ).run()
