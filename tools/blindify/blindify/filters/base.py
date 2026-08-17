from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from PIL import Image


@dataclass(frozen=True)
class Filter:
    """A named simulation/transform applied to a rendered page image."""

    key: str
    """Stable identifier used on the CLI, e.g. "protanopia"."""

    label: str
    """Human-readable label drawn at the top of the output page."""

    apply: Callable[[Image.Image], Image.Image]
    """Pure transform: takes an RGB image, returns a new RGB image."""
