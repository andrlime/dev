from __future__ import annotations

from blindify.filters.base import Filter as Filter
from blindify.filters.colorblind import Transformations

FILTERS: list[Filter] = [
    Filter("original", "Original / Typical Vision", Transformations.identity),
    Filter("protanomaly", "Protanomaly", Transformations.protanomaly),
    Filter("protanopia", "Protanopia", Transformations.protanopia),
    Filter("deuteranomaly", "Deuteranomaly", Transformations.deuteranomaly),
    Filter("deuteranopia", "Deuteranopia", Transformations.deuteranopia),
    Filter("tritanomaly", "Tritanomaly", Transformations.tritanomaly),
    Filter("tritanopia", "Tritanopia", Transformations.tritanopia),
    Filter("achromatomaly", "Achromatomaly", Transformations.achromatomaly),
    Filter("achromatopsia", "Achromatopsia", Transformations.achromatopsia),
]

FILTER_REGISTRY: dict[str, Filter] = {f.key: f for f in FILTERS}
