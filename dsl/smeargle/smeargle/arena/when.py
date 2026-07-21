from __future__ import annotations

from ..blocks import Block


def When[T](condition: bool, value: T, /) -> T | None:
    if not condition and isinstance(value, Block):
        # value gets constructed prior to it being passed as an arg to When,
        # so it already hasattr(suppressed)
        value.suppressed = True
    return value if condition else None
