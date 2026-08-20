from __future__ import annotations

from abc import ABC, abstractmethod


class Block(ABC):
    def __post_init__(self) -> None:
        """
        Does the following:
        1. Register self into the file-scoped Arena instance.
        2. Mark self as visible.
        """
        from ..arena import Arena  # deferred: arena imports blocks, avoid cycle

        self.suppressed = False
        Arena.get().create(self)

    def render(self) -> str | None:
        return self.to_typst() if not self.suppressed else None

    @abstractmethod
    def to_typst(self) -> str: ...
