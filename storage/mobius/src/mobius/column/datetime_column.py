from datetime import datetime

from mobius.column.column import Column, SQLiteValue


class DateTimeColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = datetime

    def serialize(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    def deserialize(self, raw: SQLiteValue) -> datetime | None:
        if raw is None:
            return None
        assert isinstance(raw, str)
        return datetime.fromisoformat(raw)
