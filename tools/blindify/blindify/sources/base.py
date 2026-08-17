from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from PIL import Image


@dataclass(frozen=True)
class SourcePage:
    image: Image.Image
    width_pt: float
    height_pt: float
    index: int


class Source(Protocol):
    def page_count(self) -> int:
        ...

    def iter_pages(self, dpi: int) -> Iterator[SourcePage]:
        ...
