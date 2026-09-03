from __future__ import annotations

from dataclasses import InitVar, dataclass

from ..formatter import Formatter
from .block import Block, Resolvable


@dataclass
class Job(Block):
    company: str
    title: str
    start: str
    until: str
    where: str
    bullets: InitVar[list[Resolvable[str]] | None] = None

    def __post_init__(self, bullets: list[Resolvable[str]] | None) -> None:
        """
        Does the following, in addition to Block.__post_init__:
        1. Flattens bullets, resolving When(...) tuples as appropriate.
        """
        super().__post_init__()
        self._bullets: list[str] = Block.resolve(bullets or [])

    def to_typst(self) -> str:
        period_expr = f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'
        bullets_expr = (
            "(" + ", ".join(f"text({Formatter.to_typst(b)})" for b in self._bullets) + ",)" if self._bullets else "()"
        )
        return (
            "#job(\n"
            f"  {Formatter.to_typst(self.company)},\n"
            f"  (({Formatter.to_typst(self.title)}, {period_expr}, "
            f"{Formatter.to_typst(self.where)}, {bullets_expr}),),\n"
            ")"
        )
