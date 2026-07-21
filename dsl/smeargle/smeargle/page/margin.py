from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Margin:
    left: int
    right: int
    top: int
    bottom: int

    def to_typst(self) -> str:
        return f"(left: {self.left}pt, right: {self.right}pt, top: {self.top}pt, bottom: {self.bottom}pt)"
