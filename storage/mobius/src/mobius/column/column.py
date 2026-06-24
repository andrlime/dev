from typing import Any, Callable

SQLiteValue = str | int | float | bytes | None


class Column:
    def __init__(
        self,
        *deps: Column,
        equals: Callable | None = None,
        default: object | None = None,
        validator: Callable[[object], bool] | None = None,
        primary_key: bool = False,
        nullable: bool = True,
        unique: bool = False,
        indexed: bool = False,
    ):
        if equals is not None and default is not None:
            raise ValueError("Column cannot have both equals and default.")
        self.name: str | None = None
        self.deps = deps
        self.equals = equals
        self.default = default
        self.validator = validator
        self.primary_key = primary_key
        self.nullable = nullable
        self.unique = unique
        self.indexed = indexed
        self.pytype: type | tuple[type, ...] | None = None

    def serialize(self, value: Any) -> SQLiteValue:
        """Convert a Python value to something sqlite3 can bind directly.
        Override when pytype isn't already str/int/float/bytes/None."""
        return value

    def deserialize(self, raw: SQLiteValue) -> Any:
        if raw is None:
            return None
        if self.pytype is not None and callable(self.pytype):
            return self.pytype(raw)  # type: ignore[call-arg]
        return raw
