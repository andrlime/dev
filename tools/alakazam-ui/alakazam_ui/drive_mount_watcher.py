from __future__ import annotations

from collections.abc import Callable

# pyrefly: ignore [missing-module-attribute]
from AppKit import NSWorkspace

# pyrefly: ignore [missing-module-attribute]
from Foundation import NSObject

_VOLUME_MOUNT_NOTIFICATION_NAME = "NSWorkspaceDidMountNotification"
_VOLUME_UNMOUNT_NOTIFICATION_NAME = "NSWorkspaceDidUnmountNotification"


class _VolumeChangeNotificationObserver(NSObject):
    def handleVolumeChangeNotification_(self, notification: object) -> None:
        on_volume_changed = getattr(self, "on_volume_changed", None)
        if on_volume_changed is not None:
            on_volume_changed()


class DriveMountWatcher:
    """Notifies a callback whenever a volume is mounted or unmounted."""

    def __init__(self, on_volume_changed: Callable[[], None]) -> None:
        self._notification_observer = _VolumeChangeNotificationObserver.alloc().init()
        self._notification_observer.on_volume_changed = on_volume_changed
        self._register_for_volume_notifications()

    def _register_for_volume_notifications(self) -> None:
        notification_center = NSWorkspace.sharedWorkspace().notificationCenter()
        for notification_name in (_VOLUME_MOUNT_NOTIFICATION_NAME, _VOLUME_UNMOUNT_NOTIFICATION_NAME):
            notification_center.addObserver_selector_name_object_(
                self._notification_observer,
                "handleVolumeChangeNotification:",
                notification_name,
                None,
            )
