from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import ClassVar

import rumps

# pyrefly: ignore [missing-module-attribute]
from AppKit import NSApplication, NSApplicationActivationPolicyAccessory

from alakazam_ui.config_store import ConfigEntry, ConfigEntryStore
from alakazam_ui.drive_mount_watcher import DriveMountWatcher
from alakazam_ui.folder_picker import FolderSelectionDialog
from alakazam_ui.status import SyncStatus
from alakazam_ui.sync_checker import DEFAULT_ALAKAZAM_CONFIG_FILENAME, SyncStatusChecker
from alakazam_ui.sync_executor import SyncExecutionError, SyncExecutor


@dataclass
class ConfigEntryMenuController:
    """Pairs a registered folder's data with the rumps menu row that displays it."""

    entry: ConfigEntry
    menu_item: rumps.MenuItem


class AlakazamMenuBarApp(rumps.App):
    """macOS menu bar app for monitoring and triggering alakazam syncs."""

    PERIODIC_RECHECK_INTERVAL_SECONDS: ClassVar[int] = 300
    EMPTY_STATE_MENU_ITEM_TITLE: ClassVar[str] = "No configs added yet"
    ADD_NEW_CONFIG_MENU_ITEM_TITLE: ClassVar[str] = "+ Add New Config"
    MANAGE_CONFIGS_MENU_ITEM_TITLE: ClassVar[str] = "Manage Configs"

    def __init__(self) -> None:
        super().__init__("Alakazam", quit_button="Quit")

        # Menu-bar-only: no Dock icon. FolderSelectionDialog briefly switches this to
        # Regular so its panel can reliably gain focus, then switches it back here.
        # sharedApplication() is what actually creates NSApp; rumps itself only calls
        # it later, inside .run(), so it must be created here before it can be configured.
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)

        self._config_entry_store = ConfigEntryStore()
        self._sync_status_checker = SyncStatusChecker()
        self._sync_executor = SyncExecutor()
        self._folder_selection_dialog = FolderSelectionDialog()
        self._background_operation_lock = threading.Lock()

        self._entry_controllers: list[ConfigEntryMenuController] = [
            self._build_controller_for_entry(entry) for entry in self._config_entry_store.load_entries()
        ]
        self._rebuild_menu()

        self._drive_mount_watcher = DriveMountWatcher(on_volume_changed=self._handle_volume_changed)
        self._periodic_recheck_timer = rumps.Timer(
            self._handle_periodic_timer_tick, self.PERIODIC_RECHECK_INTERVAL_SECONDS
        )
        self._periodic_recheck_timer.start()

        self._recheck_all_entries_in_background()

    def _build_controller_for_entry(self, entry: ConfigEntry) -> ConfigEntryMenuController:
        menu_item = rumps.MenuItem(
            self._build_entry_row_title(entry),
            callback=partial(self._handle_entry_row_clicked, entry),
        )
        return ConfigEntryMenuController(entry=entry, menu_item=menu_item)

    def _build_entry_row_title(self, entry: ConfigEntry) -> str:
        return f"{entry.folder_name}  {entry.last_status.status_dot}"

    def _rebuild_menu(self) -> None:
        menu_items: list[object] = []

        if self._entry_controllers:
            menu_items.extend(controller.menu_item for controller in self._entry_controllers)
        else:
            menu_items.append(rumps.MenuItem(self.EMPTY_STATE_MENU_ITEM_TITLE, callback=None))

        menu_items.append(None)
        menu_items.append(
            rumps.MenuItem(self.ADD_NEW_CONFIG_MENU_ITEM_TITLE, callback=self._handle_add_new_config_clicked)
        )

        if self._entry_controllers:
            menu_items.append(None)
            menu_items.append(self._build_manage_configs_menu_item())

        self.menu.clear()
        self.menu.update(menu_items)

    def _build_manage_configs_menu_item(self) -> rumps.MenuItem:
        manage_configs_menu_item = rumps.MenuItem(self.MANAGE_CONFIGS_MENU_ITEM_TITLE)
        for controller in self._entry_controllers:
            remove_entry_menu_item = rumps.MenuItem(
                f"Remove {controller.entry.folder_name}",
                callback=partial(self._handle_remove_entry_clicked, controller.entry),
            )
            manage_configs_menu_item.add(remove_entry_menu_item)
        return manage_configs_menu_item

    def _handle_entry_row_clicked(self, entry: ConfigEntry, sender: rumps.MenuItem) -> None:
        threading.Thread(target=self._sync_entry_then_recheck, args=(entry,), daemon=True).start()

    def _sync_entry_then_recheck(self, entry: ConfigEntry) -> None:
        self._apply_status_to_entry(entry, SyncStatus.CHECKING)
        with self._background_operation_lock:
            try:
                self._sync_executor.run_sync(entry.folder_path)
            except SyncExecutionError:
                self._apply_status_to_entry(entry, SyncStatus.ERROR)
                return

            self._apply_status_to_entry(entry, self._check_entry_status(entry))
            self._persist_entries()

    def _handle_add_new_config_clicked(self, sender: rumps.MenuItem) -> None:
        self._folder_selection_dialog.prompt_for_folder(self._handle_folder_selected)

    def _handle_folder_selected(self, selected_folder_path: Path | None) -> None:
        if selected_folder_path is None:
            return

        if any(controller.entry.folder_path == selected_folder_path for controller in self._entry_controllers):
            rumps.alert(title="Already added", message=f"{selected_folder_path} is already being monitored.")
            return

        config_file_path = selected_folder_path / DEFAULT_ALAKAZAM_CONFIG_FILENAME
        if not config_file_path.is_file():
            rumps.alert(
                title="No alakazam.toml found",
                message=f"{selected_folder_path} does not contain an {DEFAULT_ALAKAZAM_CONFIG_FILENAME} file.",
            )
            return

        new_entry = ConfigEntry(folder_path=selected_folder_path)
        self._entry_controllers.append(self._build_controller_for_entry(new_entry))
        self._persist_entries()
        self._rebuild_menu()

        threading.Thread(target=self._recheck_single_entry, args=(new_entry,), daemon=True).start()

    def _handle_remove_entry_clicked(self, entry: ConfigEntry, sender: rumps.MenuItem) -> None:
        should_remove = rumps.alert(
            title="Remove config",
            message=f"Stop monitoring {entry.folder_name}?",
            ok="Remove",
            cancel="Cancel",
        )
        if should_remove != 1:
            return

        self._entry_controllers = [
            controller for controller in self._entry_controllers if controller.entry.folder_path != entry.folder_path
        ]
        self._persist_entries()
        self._rebuild_menu()

    def _handle_volume_changed(self) -> None:
        self._recheck_all_entries_in_background()

    def _handle_periodic_timer_tick(self, sender: rumps.Timer) -> None:
        self._recheck_all_entries_in_background()

    def _recheck_all_entries_in_background(self) -> None:
        if self._background_operation_lock.locked():
            return
        threading.Thread(target=self._recheck_all_entries, daemon=True).start()

    def _recheck_all_entries(self) -> None:
        with self._background_operation_lock:
            for controller in self._entry_controllers:
                self._apply_status_to_entry(controller.entry, SyncStatus.CHECKING)
                self._apply_status_to_entry(controller.entry, self._check_entry_status(controller.entry))
            self._persist_entries()

    def _recheck_single_entry(self, entry: ConfigEntry) -> None:
        self._apply_status_to_entry(entry, SyncStatus.CHECKING)
        with self._background_operation_lock:
            self._apply_status_to_entry(entry, self._check_entry_status(entry))
            self._persist_entries()

    def _check_entry_status(self, entry: ConfigEntry) -> SyncStatus:
        try:
            return self._sync_status_checker.check_folder(entry.folder_path)
        except (FileNotFoundError, ValueError):  # fmt: skip
            return SyncStatus.ERROR

    def _apply_status_to_entry(self, entry: ConfigEntry, new_status: SyncStatus) -> None:
        entry.last_status = new_status
        entry.last_checked_at = datetime.now()

        controller = self._find_controller_for_entry(entry)
        if controller is not None:
            controller.menu_item.title = self._build_entry_row_title(entry)

    def _find_controller_for_entry(self, entry: ConfigEntry) -> ConfigEntryMenuController | None:
        for controller in self._entry_controllers:
            if controller.entry.folder_path == entry.folder_path:
                return controller
        return None

    def _persist_entries(self) -> None:
        self._config_entry_store.save_entries([controller.entry for controller in self._entry_controllers])


def main() -> int:
    AlakazamMenuBarApp().run()
    return 0
