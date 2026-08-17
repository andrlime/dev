from __future__ import annotations

from blindify.filters.base import Filter as Filter
from blindify.filters.colorblind import FILTERS as _COLORBLIND_FILTERS

FILTER_REGISTRY: dict[str, Filter] = {f.key: f for f in _COLORBLIND_FILTERS}
