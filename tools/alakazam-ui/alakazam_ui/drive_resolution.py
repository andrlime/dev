from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alakazam.sync import is_remote_spec


@dataclass(frozen=True)
class ConfiguredDrives:
    """The drives listed in a folder's alakazam.toml, resolved against what's currently mounted."""

    drive_names: list[str]

    @property
    def has_only_remote_drives(self) -> bool:
        return all(is_remote_spec(drive_name) for drive_name in self.drive_names)

    @property
    def first_mounted_local_drive(self) -> Path | None:
        for drive_name in self.drive_names:
            if is_remote_spec(drive_name):
                continue
            candidate_path = Path(drive_name)
            if candidate_path.is_dir():
                return candidate_path
        return None
