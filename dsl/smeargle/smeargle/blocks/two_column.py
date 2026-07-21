from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter


@dataclass
class TwoColumn:
    left: str
    right: str

    def to_typst(self) -> str:
        return f"{Formatter.to_typst(self.left)} + h(1fr) + {Formatter.to_typst(self.right)}"
