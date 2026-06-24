from mobius.blueprint import Blueprint
from mobius.schema import Schema


class Table:
    def __init__(self, source: Blueprint):
        self.schema = Schema(source)
        self.rows: list[dict] = []

    def add_row(self, **kwargs) -> dict:
        row = self.schema.resolve(**kwargs)
        has_unique = any(col.unique for col in self.schema.columns.values())
        existing = list(self.rows) if has_unique else []

        for name, col in self.schema.columns.items():
            val = row.get(name)

            if not col.nullable and val is None:
                raise ValueError(f"column \"{name}\" is not nullable but received None")

            if col.unique and val is not None:
                if any(r.get(name) == val for r in existing):
                    raise ValueError(
                        f"column \"{name}\" must be unique, but {val!r} already exists"
                    )

        self.rows.append(row)
        return row

    def all_rows(self) -> list[dict]:
        return self.rows
