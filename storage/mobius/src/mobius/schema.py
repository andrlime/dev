from collections import deque

from mobius.blueprint import Blueprint
from mobius.column.column import Column


class Schema:
    def __init__(self, source: Blueprint):
        source.schema()

        self.columns: dict[str, Column] = {}

        all_source_variables = vars(source).items()
        for name, maybe_col in all_source_variables:
            if isinstance(maybe_col, Column):
                maybe_col.name = name
                self.columns[name] = maybe_col

        all_columns = self.columns.values()

        unique_names = {col.name for col in all_columns}
        if len(unique_names) != len(all_columns):
            raise ValueError("exists multiple identically named columns")

        unique_ids = {id(col) for col in all_columns}
        if len(unique_ids) != len(all_columns):
            raise ValueError("exists multiple literally identical columns")

        for col in all_columns:
            for dep in col.deps:
                if dep not in all_columns:
                    raise ValueError(
                        f"\"{col.name}\" depends on unregistered column {dep!r}"
                    )

        for name, col in self.columns.items():
            if col.deps and col.equals is None:
                raise ValueError(f"column \"{name}\" has deps but no equals")

        self.topo_order = self._topo_sort()
        self.roots = {
            n for n, c in self.columns.items() if c.equals is None and not c.deps
        }
        self.name = type(source).__name__

    def _topo_sort(self) -> list[str]:
        in_degree = {n: 0 for n in self.columns}
        children: dict[str, list[str]] = {n: [] for n in self.columns}
        for n, col in self.columns.items():
            for dep in col.deps:
                assert dep.name is not None
                children[dep.name].append(n)
                in_degree[n] += 1

        queue = deque(n for n, d in in_degree.items() if d == 0)
        order = []
        while queue:
            n = queue.popleft()
            order.append(n)
            for child in children[n]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(order) != len(self.columns):
            raise ValueError("cycle in column graph")
        return order

    def resolve(self, **kwargs) -> dict:
        required = {n for n in self.roots if self.columns[n].default is None}

        unknown = set(kwargs) - self.roots
        if unknown:
            raise ValueError(f"unknown columns: {unknown}")

        missing = required - set(kwargs)
        if missing:
            raise ValueError(f"missing columns: {missing}")

        values = dict(kwargs)

        for name in self.roots - set(kwargs):
            default = self.columns[name].default
            values[name] = default() if callable(default) else default

        for name in self.topo_order:
            col = self.columns[name]
            if col.equals is not None:
                values[name] = col.equals(*[values[d.name] for d in col.deps])  # type: ignore[index]

        for name, value in values.items():
            col = self.columns[name]
            if (
                col.validator is not None
                and value is not None
                and not col.validator(value)
            ):
                raise ValueError(
                    f"column \"{name}\" failed validation with value {value!r}"
                )

        return values
