import signal
import threading
from types import TracebackType
from typing import Self

from .backend.base import Backend, Result
from .log import Logger

logger = Logger.get(__name__)


class ManagedVpn:
    def __init__(self, backend: Backend):
        self.backend = backend
        self._stop = threading.Event()

    def run(self) -> None:
        # Must handle these signals with destructor to avoid zombifying VPN client
        for s in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
            signal.signal(s, lambda *_: self._stop.set())

        with self:
            logger.info("VPN enabled automatically, press Ctrl+C to stop...")
            self._stop.wait()

    def __enter__(self) -> Self:
        if self.backend.connect(self._on_unexpected_exit) is Result.FAIL:
            raise RuntimeError("Failed to connect backend")

        if self.backend.set_proxy(enable=True) is Result.FAIL:
            logger.error("Proxy setup failed, disconnecting")
            self.backend.disconnect()
            raise RuntimeError("Failed to enable proxy")

        logger.info("Connected")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.backend.disconnect()
        self.backend.set_proxy(enable=False)
        logger.info("Disconnected")

    def _on_unexpected_exit(self) -> None:
        logger.error("Tunnel exited unexpectedly, resetting proxy")
        self.backend.set_proxy(enable=False)
        self._stop.set()
