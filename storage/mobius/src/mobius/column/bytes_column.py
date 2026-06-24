import base64

from mobius.column.column import Column, SQLiteValue


class BytesColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = bytes

    def serialize(self, value: bytes | None) -> str | None:
        if value is None:
            return None
        return base64.b64encode(value).decode()

    def deserialize(self, raw: SQLiteValue) -> bytes | None:
        if raw is None:
            return None
        assert isinstance(raw, str)
        return base64.b64decode(raw)
