from datetime import date

from mobius.column.column import Column, SQLiteValue


class DateColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = date

    def serialize(self, value: date | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()

    def deserialize(self, raw: SQLiteValue) -> date | None:
        if raw is None:
            return None
        assert isinstance(raw, str)
        return date.fromisoformat(raw)
