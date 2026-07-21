from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .block import Block


@dataclass
class Award(Block):
    title: str
    organisation: str

    def _to_typst(self) -> str:
        return f"#award({Formatter.to_typst(self.title)}, {Formatter.to_typst(self.organisation)})"
