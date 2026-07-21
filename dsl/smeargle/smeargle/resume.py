from __future__ import annotations

from dataclasses import dataclass, field

from .arena import Arena
from .blocks import Block
from .page import PageConfig


@dataclass
class Resume:
    page: PageConfig
    blocks: list[Block] = field(default_factory=list)

    @classmethod
    def from_arena(cls, page: PageConfig) -> Resume:
        return cls(page=page, blocks=Arena.get().drain())

    def to_typst(self) -> str:
        parts = [self.page.to_typst(), *(block.to_typst() for block in self.blocks)]
        return "\n".join(part for part in parts if part)
