from __future__ import annotations

from ..blocks import Block


class Arena:
    """
    Idempotent arena-like storage for resume components.
    This is essentially just a singleton queue with a fancy hat.
    """

    instance: Arena | None = None

    def __init__(self) -> None:
        self._items: list[Block] = []

    @staticmethod
    def get() -> Arena:
        if Arena.instance is None:
            Arena.instance = Arena()
        return Arena.instance

    def create(self, block: Block, /) -> None:
        if not any(existing is block for existing in self._items):
            self._items.append(block)

    def drain(self) -> list[Block]:
        items, self._items = self._items, []
        return items

    def reset(self) -> None:
        self._items = []
