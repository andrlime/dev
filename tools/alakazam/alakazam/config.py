from __future__ import annotations

import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from alakazam.remote_sync import RemoteSync

DEFAULT_IGNORE_LIST = [".venv", ".claude", ".DS_Store", "__pycache__"]
MANAGED_RSYNC_FIELDS = {"source", "destination", "dry_run", "exclude"}
VALID_RSYNC_FIELDS = {f.name for f in dataclasses.fields(RemoteSync)} - MANAGED_RSYNC_FIELDS


@dataclass
class AlakazamConfig:
    drive_path: str
    drive_name: list[str]
    ignore_list: list[str] = field(default_factory=list)
    rsync_options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> AlakazamConfig:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        drive_path = data.get("drive_path")
        if drive_path is None:
            raise ValueError("Config missing required field: 'drive_path'")

        drive_name = data.get("drive_name")
        if not drive_name:
            raise ValueError("Config missing required field: 'drive_name'")
        if isinstance(drive_name, str):
            drive_name = [drive_name]
        elif not isinstance(drive_name, list) or not all(isinstance(entry, str) for entry in drive_name):
            raise ValueError("Config field 'drive_name' must be a string or a list of strings")

        ignore_list = DEFAULT_IGNORE_LIST + [
            pattern for pattern in data.get("ignore_list", []) if pattern not in DEFAULT_IGNORE_LIST
        ]

        rsync_options = data.get("rsync", {})
        managed = sorted(MANAGED_RSYNC_FIELDS & rsync_options.keys())
        if managed:
            raise ValueError(f"Config field 'rsync' cannot override: {', '.join(managed)}")
        unknown = sorted(rsync_options.keys() - VALID_RSYNC_FIELDS)
        if unknown:
            raise ValueError(f"Config field 'rsync' has unknown option(s): {', '.join(unknown)}")

        return cls(
            drive_path=drive_path,
            drive_name=drive_name,
            ignore_list=ignore_list,
            rsync_options=rsync_options,
        )
