from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_IGNORE_LIST = [".venv", ".claude", ".DS_Store", "__pycache__"]


@dataclass
class AlakazamConfig:
    drive_path: str
    drive_name: list[str]
    ignore_list: list[str] = field(default_factory=list)

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

        ignore_list = DEFAULT_IGNORE_LIST + [
            pattern for pattern in data.get("ignore_list", []) if pattern not in DEFAULT_IGNORE_LIST
        ]

        return cls(drive_path=drive_path, drive_name=drive_name, ignore_list=ignore_list)
