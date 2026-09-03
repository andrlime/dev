from __future__ import annotations

from ..blocks import Block


def When[T](condition: bool, *values: T) -> tuple[T | None, ...]:
    if not condition:
        for value in values:
            if isinstance(value, Block):
                # value gets constructed prior to it being passed as an arg to When,
                # so it already hasattr(suppressed)
                value.suppressed = True
        return (None,) * len(values)
    return values
