from __future__ import annotations

from dataclasses import InitVar, dataclass

from ..formatter import Formatter
from .block import Block, Resolvable
from .degree import Degree


@dataclass
class School(Block):
    name: str
    start: str | None
    until: str
    where: str
    degrees: InitVar[list[Resolvable[Degree]] | None] = None
    gpa: str | None = None

    def __post_init__(self, degrees: list[Resolvable[Degree]] | None) -> None:
        """
        Does the following, in addition to Block.__post_init__:
        1. Flattens degrees, resolving When(...) tuples as appropriate.
        """
        super().__post_init__()
        self._degrees: list[Degree] = Block.resolve(degrees or [])

    def to_typst(self) -> str:
        def period_expr():
            if self.start == self.until or self.start == "" or self.start is None:
                return f"{Formatter.to_typst(self.until)}"
            assert self.start is not None
            return f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'

        def degree_expr():
            if not self._degrees:
                return '""'
            entries = ",\n    ".join(degree.to_typst() for degree in self._degrees)
            return f"(\n    {entries},\n  )"

        gpa_expr = Formatter.to_typst(self.gpa) if self.gpa else '""'

        return (
            "#school(\n"
            f"  {Formatter.to_typst(self.name)},\n"
            f"  {period_expr()},\n"
            f"  {degree_expr()},\n"
            f"  {Formatter.to_typst(self.where)},\n"
            f"  {gpa_expr},\n"
            ")"
        )
