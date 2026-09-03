from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

type Resolvable[T] = T | tuple[T | None, ...] | None


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

    @staticmethod
    def resolve[T](items: Iterable[Resolvable[T]]) -> list[T]:
        """
        Flattens and resolves potentially variadic When(condition, stuff...) clauses.
        """
        result: list[T] = []
        for item in items:
            if isinstance(item, tuple):
                result.extend(x for x in item if x is not None)
            elif item is not None:
                result.append(item)
        return result

    @abstractmethod
    def to_typst(self) -> str: ...
