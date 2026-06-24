import subprocess
import threading
from collections.abc import Callable

from ..log import get_logger
from .base import Result, State

logger = get_logger(__name__)


class SensibleDefaultBackend:
    def __init__(self, label: str, host: str, port: int, iface: str = "Wi-Fi"):
        self.label = label
        self.host = host
        self.port = port
        self.iface = iface
        self._process: subprocess.Popen | None = None
        logger.info(
            f"Instantiated SensibleDefaultBackend({label}) to {host}:{port} for interface {iface}"
        )

    @staticmethod
    def _emoji_of_state(state: State) -> str:
        match state:
            case State.CONNECTING:
                return "🟨"
            case State.CONNECTED:
                return "🟩"
            case State.DISCONNECTED | State.FAILED:
                return "🟥"

    def format_title(self, state: State) -> str:
        suffix = " (failed)" if state is State.FAILED else ""
        return f"{self._emoji_of_state(state)} {self.label}{suffix}"

    def connect(self, on_unexpected_exit: Callable[[], None]) -> Result:
        if self._process:
            logger.warning("Already connected, ignoring connect request")
            return Result.FAIL

        logger.info("Connecting to %s:%d", self.host, self.port)
        try:
            self._process = subprocess.Popen(
                ["ssh", "-ND", str(self.port), self.host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        except OSError as e:
            logger.error("Failed to start tunnel: %s", e)
            return Result.FAIL

        threading.Thread(
            target=self._watch, args=(on_unexpected_exit,), daemon=True
        ).start()

        logger.info("Tunnel established (pid %d)", self._process.pid)
        return Result.OK

    def disconnect(self) -> Result:
        if self._process:
            logger.info("Terminating tunnel (pid %d)", self._process.pid)
            self._process.terminate()
            self._process = None

        return Result.OK

    def _watch(self, on_unexpected_exit: Callable[[], None]) -> None:
        assert self._process is not None, "Cannot watch a None process"
        self._process.wait()
        if self._process is not None:
            self._process = None
            on_unexpected_exit()

    def _run(self, *args: str) -> None:
        result = subprocess.run(list(args), capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(
                f"`{' '.join(args)}` failed (exit {result.returncode}): {result.stderr.strip()}"
            )

    def set_proxy(self, *, enable: bool) -> Result:
        try:
            if enable:
                logger.debug(
                    "Enabling SOCKS proxy on %s at 127.0.0.1:%d", self.iface, self.port
                )
                self._run(
                    "networksetup",
                    "-setsocksfirewallproxy",
                    self.iface,
                    "127.0.0.1",
                    str(self.port),
                )
                self._run(
                    "networksetup", "-setsocksfirewallproxystate", self.iface, "on"
                )
            else:
                logger.debug("Disabling SOCKS proxy on %s", self.iface)
                self._run(
                    "networksetup", "-setsocksfirewallproxystate", self.iface, "off"
                )

        except RuntimeError as e:
            logger.error("Failed to update proxy settings: %s", e)
            return Result.FAIL

        return Result.OK
