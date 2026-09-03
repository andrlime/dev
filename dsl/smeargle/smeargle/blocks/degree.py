from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter


@dataclass
class Degree:
    title: str
    major: str
    note: str | None = None

    def to_typst(self) -> str:
        expr = f'{Formatter.to_typst(self.title)} + ", " + {Formatter.to_typst(self.major)}'
        if self.note:
            expr += f' + " (" + {Formatter.to_typst(self.note)} + ")"'
        return expr
