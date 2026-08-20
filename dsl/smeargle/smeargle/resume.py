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
        rendered = (block.render() for block in self.blocks)
        parts = [self.page.to_typst(), *(part for part in rendered if part is not None)]
        return "\n".join(parts)
