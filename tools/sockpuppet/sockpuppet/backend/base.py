from collections.abc import Callable
from enum import StrEnum
from typing import Protocol


class State(StrEnum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    FAILED = "failed"


class Result(StrEnum):
    OK = "ok"
    FAIL = "fail"


class Backend(Protocol):
    def format_title(self, state: State) -> str: ...
    def connect(self, on_unexpected_exit: Callable[[], None]) -> Result: ...
    def disconnect(self) -> Result: ...
    def set_proxy(self, *, enable: bool) -> Result: ...
