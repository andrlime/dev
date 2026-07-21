from __future__ import annotations

from dataclasses import dataclass

from ..formatter import Formatter
from .block import Block


@dataclass
class Project(Block):
    title: str
    start: str
    until: str
    bullets: list[str]
    organisation: str | None = None

    def _to_typst(self) -> str:
        if self.start == self.until:
            period_expr = Formatter.to_typst(self.start)
        else:
            period_expr = f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'
        organisation_expr = Formatter.to_typst(self.organisation) if self.organisation else '""'
        bullets_expr = "(" + ", ".join(f"text({Formatter.to_typst(b)})" for b in self.bullets) + ",)"
        return (
            "#project(\n"
            f"  {Formatter.to_typst(self.title)},\n"
            f"  {organisation_expr},\n"
            f"  {period_expr},\n"
            f"  {bullets_expr},\n"
            ")"
        )
