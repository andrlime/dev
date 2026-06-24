import json

from mobius.column.column import Column, SQLiteValue


class JsonColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = (dict, list)

    def serialize(self, value: dict | list | None) -> str | None:
        if value is None:
            return None
        return json.dumps(value)

    def deserialize(self, raw: SQLiteValue) -> dict | list | None:
        if raw is None:
            return None
        assert isinstance(raw, str | bytes)
        return json.loads(raw)
