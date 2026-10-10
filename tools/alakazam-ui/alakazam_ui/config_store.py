from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from alakazam_ui.status import SyncStatus


@dataclass
class ConfigEntry:
    """A single folder the user has registered for monitoring, plus its last known status."""

    folder_path: Path
    last_status: SyncStatus = SyncStatus.UNKNOWN
    last_checked_at: datetime | None = None

    @property
    def folder_name(self) -> str:
        return self.folder_path.name

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "folder_path": str(self.folder_path),
            "last_status": self.last_status.value,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at is not None else None,
        }

    @classmethod
    def from_json_dict(cls, raw_entry: dict[str, Any]) -> ConfigEntry:
        raw_last_checked_at = raw_entry.get("last_checked_at")
        return cls(
            folder_path=Path(raw_entry["folder_path"]),
            last_status=SyncStatus(raw_entry.get("last_status", SyncStatus.UNKNOWN.value)),
            last_checked_at=datetime.fromisoformat(raw_last_checked_at) if raw_last_checked_at else None,
        )


class ConfigEntryStore:
    """Reads and writes the list of registered folders to ~/.alakazam-config."""

    def __init__(self, store_file_path: Path | None = None) -> None:
        self._store_file_path = store_file_path if store_file_path is not None else self.default_store_file_path()

    @staticmethod
    def default_store_file_path() -> Path:
        return Path.home() / ".alakazam-config"

    def load_entries(self) -> list[ConfigEntry]:
        if not self._store_file_path.exists():
            return []

        raw_document = json.loads(self._store_file_path.read_text())
        raw_entries = raw_document.get("entries", [])
        return [ConfigEntry.from_json_dict(raw_entry) for raw_entry in raw_entries]

    def save_entries(self, entries: list[ConfigEntry]) -> None:
        serializable_document = {"entries": [entry.to_json_dict() for entry in entries]}
        self._store_file_path.write_text(json.dumps(serializable_document, indent=2))
