from __future__ import annotations

from dataclasses import dataclass, field

from ..formatter import Formatter
from .block import Block


@dataclass
class Job(Block):
    company: str
    title: str
    start: str
    until: str
    where: str
    bullets: list[str | None] = field(default_factory=list)

    def __post_init__(self) -> None:
        """
        Does the following, in addition to Block.__post_init__:
        1. Strips None entries out of bullets (When(...) resolving false).
        """
        super().__post_init__()
        self.bullets = [b for b in self.bullets if b is not None]

    def _to_typst(self) -> str:
        period_expr = f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'
        bullets_expr = (
            "(" + ", ".join(f"text({Formatter.to_typst(b)})" for b in self.bullets if b is not None) + ",)"
            if self.bullets
            else "()"
        )
        return (
            "#job(\n"
            f"  {Formatter.to_typst(self.company)},\n"
            f"  (({Formatter.to_typst(self.title)}, {period_expr}, "
            f"{Formatter.to_typst(self.where)}, {bullets_expr}),),\n"
            ")"
        )
