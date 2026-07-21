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

    def _to_typst(self) -> str:
        item_exprs = []
        for item in self.items:
            expr = item.to_typst() if isinstance(item, TwoColumn) else Formatter.to_typst(item)
            item_exprs.append(f"text({expr})")
        return f'#tags(\n  "{Escape.string(self.label)}",\n  (' + ", ".join(item_exprs) + ",),\n)"
