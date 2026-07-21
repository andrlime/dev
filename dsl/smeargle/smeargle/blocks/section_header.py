from __future__ import annotations

from dataclasses import dataclass

from ..escape import Escape
from .block import Block


@dataclass
class SectionHeader(Block):
    title: str

    def _to_typst(self) -> str:
        return f'#section("{Escape.string(self.title)}")'
