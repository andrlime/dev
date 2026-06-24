from abc import ABC, abstractmethod

from mobius.schema import Schema


class StorageBackend(ABC):
    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    @abstractmethod
    def insert(self, row: dict) -> None: ...

    @abstractmethod
    def read_all(self) -> list[dict]: ...

    @abstractmethod
    def delete_all(self) -> None: ...

    def add_row(self, **kwargs) -> dict:
        row = self.schema.resolve(**kwargs)
        self._check_row(row)
        self.insert(row)
        return row

    def _check_row(self, row: dict) -> None:
        has_unique = any(col.unique for col in self.schema.columns.values())
        existing = self.read_all() if has_unique else []
        for name, col in self.schema.columns.items():
            val = row.get(name)
            if not col.nullable and val is None:
                raise ValueError(f"column \"{name}\" is not nullable but received None")
            if col.unique and val is not None:
                if any(r.get(name) == val for r in existing):
                    raise ValueError(
                        f"column \"{name}\" must be unique, but {val!r} already exists"
                    )

    def count(self) -> int:
        return len(self.read_all())

    def find(self, **kwargs) -> list[dict]:
        return [
            row
            for row in self.read_all()
            if all(row.get(k) == v for k, v in kwargs.items())
        ]
