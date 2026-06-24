import uuid

from mobius.column.column import Column, SQLiteValue


class UuidColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        if "equals" not in kwargs:
            kwargs.setdefault("default", lambda: uuid.uuid4())
        super().__init__(*deps, **kwargs)
        self.pytype = uuid.UUID

    def serialize(self, value: uuid.UUID | None) -> str | None:
        if value is None:
            return None
        return str(value)

    def deserialize(self, raw: SQLiteValue) -> uuid.UUID | None:
        if raw is None:
            return None
        assert isinstance(raw, str)
        return uuid.UUID(raw)
