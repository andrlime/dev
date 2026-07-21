from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .block import Block
from .degree import Degree


@dataclass
class School(Block):
    name: str
    start: str | None
    until: str
    where: str
    degrees: list[Degree]
    gpa: str | None = None

    def _to_typst(self) -> str:
        def period_expr():
            if self.start == self.until or self.start == "" or self.start is None:
                return f"{Formatter.to_typst(self.until)}"
            assert self.start is not None
            return f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'

        degree_expr = ' + "; " + '.join(degree.to_typst() for degree in self.degrees) if self.degrees else '""'
        gpa_expr = Formatter.to_typst(self.gpa) if self.gpa else '""'

        return (
            "#school(\n"
            f"  {Formatter.to_typst(self.name)},\n"
            f"  {period_expr()},\n"
            f"  {degree_expr},\n"
            f"  {Formatter.to_typst(self.where)},\n"
            f"  {gpa_expr},\n"
            ")"
        )
