from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class Filter:
    key: str
    label: str
    apply: Callable[[Image.Image], Image.Image]
