from __future__ import annotations

from dataclasses import dataclass

from ..escape import Escape
from ..formatter import Formatter
from .block import Block
from .two_column import TwoColumn


@dataclass
class ListBlock(Block):
    label: str
    items: list[str | TwoColumn]

    def to_typst(self) -> str:
        def item_expr(item: str | TwoColumn) -> str:
            expr = item.to_typst() if isinstance(item, TwoColumn) else Formatter.to_typst(item)
            return f"text({expr})"

        item_exprs = [item_expr(item) for item in self.items]
        return f'#tags(\n  "{Escape.string(self.label)}",\n  (' + ", ".join(item_exprs) + ",),\n)"
