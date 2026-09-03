from __future__ import annotations

from dataclasses import InitVar, dataclass

from ..formatter import Formatter
from .block import Block, Resolvable


@dataclass
class Project(Block):
    title: str
    start: str
    until: str
    bullets: InitVar[list[Resolvable[str]]]
    organisation: str | None = None

    def __post_init__(self, bullets: list[Resolvable[str]]) -> None:
        """
        Does the following, in addition to Block.__post_init__:
        1. Flattens bullets, resolving When(...) tuples as appropriate.
        """
        super().__post_init__()
        self._bullets: list[str] = Block.resolve(bullets)

    def to_typst(self) -> str:
        if self.start == self.until:
            period_expr = Formatter.to_typst(self.start)
        else:
            period_expr = f'{Formatter.to_typst(self.start)} + " – " + {Formatter.to_typst(self.until)}'
        organisation_expr = Formatter.to_typst(self.organisation) if self.organisation else '""'
        bullets_expr = "(" + ", ".join(f"text({Formatter.to_typst(b)})" for b in self._bullets) + ",)"
        return (
            "#project(\n"
            f"  {Formatter.to_typst(self.title)},\n"
            f"  {organisation_expr},\n"
            f"  {period_expr},\n"
            f"  {bullets_expr},\n"
            ")"
        )
