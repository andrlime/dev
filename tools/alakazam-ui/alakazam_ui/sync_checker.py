from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from alakazam.config import AlakazamConfig
from alakazam.remote_sync import RemoteSync

from alakazam_ui.drive_resolution import ConfiguredDrives
from alakazam_ui.status import SyncStatus

DEFAULT_ALAKAZAM_CONFIG_FILENAME = "alakazam.toml"

# Fields from RemoteSync that affect WHAT counts as changed (content/deletion semantics),
# as opposed to WHICH metadata a real sync preserves. Only these are carried over from a
# folder's own rsync_options into the dry-run diff used for status checking.
_CONTENT_SIGNIFICANT_RSYNC_OPTION_NAMES: frozenset[str] = frozenset(
    {
        "checksum",
        "size_only",
        "ignore_times",
        "update",
        "existing",
        "ignore_existing",
        "delete",
        "delete_before",
        "delete_during",
        "delete_after",
        "delete_excluded",
        "remove_source_files",
        "force",
        "include",
        "include_from",
        "filter_rules",
        "max_size",
        "min_size",
    }
)


class SyncStatusCheckError(RuntimeError):
    """Raised when rsync itself fails while diffing a folder against its drive."""


@dataclass(frozen=True)
class SyncStatusChecker:
    """Determines a folder's SyncStatus by asking rsync for a dry-run diff, rather than
    re-implementing rsync's own change-detection logic with a hand-rolled hash.

    The diff deliberately ignores permissions/ownership and uses a tolerant modify-window,
    rather than mirroring the real sync's own archive attributes exactly: many external
    drives (FAT32/exFAT in particular) can't store Unix permissions or sub-second mtimes
    at all, so comparing those would report every file as "changed" forever, even right
    after a real sync completes.
    """

    config_filename: str = DEFAULT_ALAKAZAM_CONFIG_FILENAME
    modify_window_seconds: ClassVar[int] = 2

    def check_folder(self, folder_path: Path) -> SyncStatus:
        alakazam_config = AlakazamConfig.load(folder_path / self.config_filename)
        configured_drives = ConfiguredDrives(alakazam_config.drive_name)

        if configured_drives.has_only_remote_drives:
            return SyncStatus.SSH_ONLY

        mounted_local_drive = configured_drives.first_mounted_local_drive
        if mounted_local_drive is None:
            return SyncStatus.DRIVE_MISSING

        destination_path = mounted_local_drive / alakazam_config.drive_path
        try:
            dry_run_output = self._capture_dry_run_diff(folder_path, destination_path, alakazam_config)
        except SyncStatusCheckError:
            return SyncStatus.ERROR

        return SyncStatus.OUT_OF_SYNC if dry_run_output.strip() else SyncStatus.IN_SYNC

    def _capture_dry_run_diff(
        self,
        source_path: Path,
        destination_path: Path,
        alakazam_config: AlakazamConfig,
    ) -> str:
        dry_run_options = {
            option_name: option_value
            for option_name, option_value in alakazam_config.rsync_options.items()
            if option_name in _CONTENT_SIGNIFICANT_RSYNC_OPTION_NAMES
        }
        dry_run_options.update(
            dry_run=True,
            itemize_changes=True,
            verbose=False,
            stats=False,
            progress=False,
            mkpath=True,
            archive=False,
            recursive=True,
            links=True,
            times=True,
            perms=False,
            group=False,
            owner=False,
            extra_args=[
                *alakazam_config.rsync_options.get("extra_args", []),
                f"--modify-window={self.modify_window_seconds}",
            ],
        )

        dry_run_command = RemoteSync(
            source=source_path,
            destination=destination_path,
            exclude=alakazam_config.ignore_list,
            **dry_run_options,
        ).build_command()

        try:
            completed_process = subprocess.run(
                dry_run_command,
                check=True,
                capture_output=True,
                text=True,
            )
        except (subprocess.CalledProcessError, OSError) as error:
            raise SyncStatusCheckError(f"rsync dry-run failed for {source_path}: {error}") from error

        return completed_process.stdout
