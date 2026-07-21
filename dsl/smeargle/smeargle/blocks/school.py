from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .block import Block
from .degree import Degree


@dataclass
class School(Block):
    name: str
    start: str
    until: str
    where: str
    degrees: list[Degree]
    gpa: str | None = None

    def _to_typst(self) -> str:
        degree_expr = ' + "; " + '.join(degree.to_typst() for degree in self.degrees) if self.degrees else '""'
        period_expr = f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'
        gpa_expr = Formatter.to_typst(self.gpa) if self.gpa else '""'
        return (
            "#school(\n"
            f"  {Formatter.to_typst(self.name)},\n"
            f"  {period_expr},\n"
            f"  {degree_expr},\n"
            f"  {Formatter.to_typst(self.where)},\n"
            f"  {gpa_expr},\n"
            ")"
        )
