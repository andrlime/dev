from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

# pyrefly: ignore [missing-module-attribute]
from AppKit import NSApp, NSApplicationActivationPolicyAccessory, NSApplicationActivationPolicyRegular, NSOpenPanel
from PyObjCTools import AppHelper

_OPEN_PANEL_OK_RESPONSE_CODE = 1
_ACTIVATION_SETTLE_DELAY_SECONDS = 0.05


class FolderSelectionDialog:
    """Wraps the native macOS folder-picker (NSOpenPanel) used by "+ Add New Config"."""

    def prompt_for_folder(self, on_folder_selected: Callable[[Path | None], None]) -> None:
        NSApp.setActivationPolicy_(NSApplicationActivationPolicyRegular)
        NSApp.activateIgnoringOtherApps_(True)
        AppHelper.callLater(_ACTIVATION_SETTLE_DELAY_SECONDS, self._show_panel, on_folder_selected)

    def _show_panel(self, on_folder_selected: Callable[[Path | None], None]) -> None:
        open_panel = NSOpenPanel.openPanel()
        open_panel.setTitle_("Select a folder containing alakazam.toml")
        open_panel.setCanChooseDirectories_(True)
        open_panel.setCanChooseFiles_(False)
        open_panel.setAllowsMultipleSelection_(False)
        open_panel.setResolvesAliases_(True)

        def handle_completion(response_code: int) -> None:
            NSApp.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            on_folder_selected(self._resolve_selected_folder(open_panel, response_code))

        open_panel.beginWithCompletionHandler_(handle_completion)
        open_panel.makeKeyAndOrderFront_(None)

    def _resolve_selected_folder(self, open_panel: NSOpenPanel, response_code: int) -> Path | None:
        if response_code != _OPEN_PANEL_OK_RESPONSE_CODE:
            return None

        selected_urls = open_panel.URLs()
        if not selected_urls:
            return None

        return Path(str(selected_urls[0].path()))
