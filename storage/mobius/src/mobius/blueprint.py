from typing import Protocol, runtime_checkable


@runtime_checkable
class Blueprint(Protocol):
    def schema(self) -> None: ...
