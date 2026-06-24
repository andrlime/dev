import rumps

from .backend.base import Backend, Result, State
from .log import get_logger

logger = get_logger(__name__)


class VpnApp(rumps.App):
    def __init__(self, backend: Backend):
        self._backend = backend
        super().__init__(backend.format_title(State.DISCONNECTED))
        self.menu = ["Connect", "Disconnect"]

    @rumps.clicked("Connect")
    def connect(self, _):
        self.title = self._backend.format_title(State.CONNECTING)

        if self._backend.connect(self._on_unexpected_exit) is Result.FAIL:
            self.title = self._backend.format_title(State.FAILED)
            return

        if self._backend.set_proxy(enable=True) is Result.FAIL:
            logger.error("Proxy setup failed, disconnecting")
            self.disconnect(None)
            return

        logger.info("Connected")
        self.title = self._backend.format_title(State.CONNECTED)

    @rumps.clicked("Disconnect")
    def disconnect(self, _):
        self._backend.disconnect()
        self._backend.set_proxy(enable=False)
        self.title = self._backend.format_title(State.DISCONNECTED)
        logger.info("Disconnected")

    def _on_unexpected_exit(self) -> None:
        logger.error("Tunnel exited unexpectedly")
        self.title = self._backend.format_title(State.FAILED)
