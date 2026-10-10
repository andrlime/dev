from __future__ import annotations

from enum import StrEnum


class SyncStatus(StrEnum):
    """The sync state of a single configured folder, as shown by its menu bar dot."""

    UNKNOWN = "unknown"
    CHECKING = "checking"
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    DRIVE_MISSING = "drive_missing"
    SSH_ONLY = "ssh_only"
    ERROR = "error"

    @property
    def status_dot(self) -> str:
        """A single-glyph marker suitable for display in a menu bar title."""
        status_dot_by_status = {
            SyncStatus.UNKNOWN: "⚪",
            SyncStatus.CHECKING: "⏳",
            SyncStatus.IN_SYNC: "🟢",
            SyncStatus.OUT_OF_SYNC: "🟡",
            SyncStatus.DRIVE_MISSING: "🔴",
            SyncStatus.SSH_ONLY: "🟣",
            SyncStatus.ERROR: "⚠️",
        }
        return status_dot_by_status[self]
