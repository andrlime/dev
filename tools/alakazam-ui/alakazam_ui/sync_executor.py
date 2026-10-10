from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alakazam.config import AlakazamConfig
from alakazam.sync import sync as run_alakazam_sync

from alakazam_ui.sync_checker import DEFAULT_ALAKAZAM_CONFIG_FILENAME


class SyncExecutionError(RuntimeError):
    """Raised when a real (non-dry-run) sync fails."""


@dataclass(frozen=True)
class SyncExecutor:
    config_filename: str = DEFAULT_ALAKAZAM_CONFIG_FILENAME

    def run_sync(self, folder_path: Path) -> None:
        try:
            alakazam_config = AlakazamConfig.load(folder_path / self.config_filename)
            run_alakazam_sync(folder_path, alakazam_config, dry_run=False)
        except (FileNotFoundError, ValueError) as error:
            raise SyncExecutionError(f"sync failed for {folder_path}: {error}") from error
