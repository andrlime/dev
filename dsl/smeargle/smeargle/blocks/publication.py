from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .block import Block


@dataclass
class Publication(Block):
    citation: str

    def _to_typst(self) -> str:
        return f"#pub({Formatter.to_typst(self.citation)})"
