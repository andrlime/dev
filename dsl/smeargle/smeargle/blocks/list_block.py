from __future__ import annotations

from dataclasses import InitVar, dataclass

from ..escape import Escape
from ..formatter import Formatter
from .block import Block, Resolvable
from .two_column import TwoColumn


@dataclass
class ListBlock(Block):
    label: str
    items: InitVar[list[Resolvable[str | TwoColumn]]]

    def __post_init__(self, items: list[Resolvable[str | TwoColumn]]) -> None:
        """
        Does the following, in addition to Block.__post_init__:
        1. Flattens items, resolving When(...) tuples as appropriate.
        """
        super().__post_init__()
        self._items: list[str | TwoColumn] = Block.resolve(items)

    def to_typst(self) -> str:
        def item_expr(item: str | TwoColumn) -> str:
            expr = item.to_typst() if isinstance(item, TwoColumn) else Formatter.to_typst(item)
            return f"text({expr})"

        item_exprs = [item_expr(item) for item in self._items]
        return f'#tags(\n  "{Escape.string(self.label)}",\n  (' + ", ".join(item_exprs) + ",),\n)"
