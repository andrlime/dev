import uuid
from datetime import date, datetime

import pytest

from mobius.column import (
    BoolColumn,
    BytesColumn,
    Column,
    DateColumn,
    DateTimeColumn,
    FloatColumn,
    IntColumn,
    JsonColumn,
    StringColumn,
    UuidColumn,
)


class TestColumnBase:
    def test_name_is_none_initially(self):
        col = IntColumn()
        assert col.name is None

    def test_name_can_be_assigned(self):
        col = IntColumn()
        col.name = "age"
        assert col.name == "age"

    def test_no_deps_by_default(self):
        col = IntColumn()
        assert col.deps == ()

    def test_deps_stored(self):
        a = IntColumn()
        b = IntColumn()
        c = IntColumn(a, b, equals=lambda x, y: x + y)
        assert c.deps == (a, b)

    def test_equals_and_default_raises(self):
        with pytest.raises(ValueError, match="cannot have both"):
            IntColumn(equals=lambda: 0, default=0)

    def test_equals_stored(self):
        def fn(x):
            return x * 2

        col = IntColumn(equals=fn)
        assert col.equals is fn

    def test_default_stored(self):
        col = IntColumn(default=42)
        assert col.default == 42

    def test_validator_stored(self):
        def fn(v):
            return v > 0

        col = IntColumn(validator=fn)
        assert col.validator is fn

    def test_flags_default(self):
        col = IntColumn()
        assert col.primary_key is False
        assert col.nullable is True
        assert col.unique is False
        assert col.indexed is False

    def test_flags_set(self):
        col = IntColumn(primary_key=True, nullable=False, unique=True, indexed=True)
        assert col.primary_key is True
        assert col.nullable is False
        assert col.unique is True
        assert col.indexed is True

    def test_serialize_passthrough(self):
        col = Column()
        assert col.serialize(42) == 42
        assert col.serialize("hello") == "hello"
        assert col.serialize(None) is None

    def test_deserialize_passthrough(self):
        col = Column()
        assert col.deserialize(42) == 42
        assert col.deserialize("hello") == "hello"
        assert col.deserialize(None) is None


class TestBoolColumn:
    def test_pytype(self):
        assert BoolColumn().pytype is bool

    def test_serialize_true(self):
        assert BoolColumn().serialize(True) == 1

    def test_serialize_false(self):
        assert BoolColumn().serialize(False) == 0

    def test_serialize_none_returns_none(self):
        assert BoolColumn().serialize(None) is None

    def test_deserialize_truthy(self):
        assert BoolColumn().deserialize(1) is True

    def test_deserialize_falsy(self):
        assert BoolColumn().deserialize(0) is False

    def test_deserialize_any_truthy_int(self):
        # bool() treats any non-zero int as True, not just 1
        assert BoolColumn().deserialize(2) is True
        assert BoolColumn().deserialize(-1) is True

    def test_roundtrip(self):
        col = BoolColumn()
        assert col.deserialize(col.serialize(True)) is True
        assert col.deserialize(col.serialize(False)) is False


class TestDateColumn:
    def test_pytype(self):
        assert DateColumn().pytype is date

    def test_serialize(self):
        assert DateColumn().serialize(date(2024, 3, 15)) == "2024-03-15"

    def test_serialize_none_returns_none(self):
        assert DateColumn().serialize(None) is None

    def test_deserialize(self):
        assert DateColumn().deserialize("2024-03-15") == date(2024, 3, 15)

    def test_deserialize_none_returns_none(self):
        assert DateColumn().deserialize(None) is None

    def test_roundtrip(self):
        col = DateColumn()
        d = date(2024, 3, 15)
        assert col.deserialize(col.serialize(d)) == d


class TestDateTimeColumn:
    def test_pytype(self):
        assert DateTimeColumn().pytype is datetime

    def test_serialize(self):
        dt = datetime(2024, 3, 15, 12, 30, 0)
        assert DateTimeColumn().serialize(dt) == "2024-03-15T12:30:00"

    def test_serialize_none_returns_none(self):
        assert DateTimeColumn().serialize(None) is None

    def test_deserialize(self):
        result = DateTimeColumn().deserialize("2024-03-15T12:30:00")
        assert result == datetime(2024, 3, 15, 12, 30, 0)

    def test_deserialize_none_returns_none(self):
        assert DateTimeColumn().deserialize(None) is None

    def test_roundtrip(self):
        col = DateTimeColumn()
        dt = datetime(2024, 3, 15, 12, 30, 45)
        assert col.deserialize(col.serialize(dt)) == dt


class TestFloatColumn:
    def test_pytype(self):
        assert FloatColumn().pytype is float

    def test_serialize_passthrough(self):
        assert FloatColumn().serialize(3.14) == 3.14

    def test_deserialize_coerces_int_to_float(self):
        assert FloatColumn().deserialize(1) == 1.0
        assert isinstance(FloatColumn().deserialize(1), float)

    def test_deserialize_none_returns_none(self):
        assert FloatColumn().deserialize(None) is None


class TestIntColumn:
    def test_pytype(self):
        assert IntColumn().pytype is int

    def test_serialize_passthrough(self):
        assert IntColumn().serialize(42) == 42

    def test_deserialize_coerces_string(self):
        assert IntColumn().deserialize("42") == 42

    def test_deserialize_none_returns_none(self):
        assert IntColumn().deserialize(None) is None


class TestJsonColumn:
    def test_pytype(self):
        assert JsonColumn().pytype == (dict, list)

    def test_serialize_dict(self):
        import json

        result = JsonColumn().serialize({"key": "value"})
        assert result is not None
        assert json.loads(result) == {"key": "value"}

    def test_serialize_none_returns_none(self):
        assert JsonColumn().serialize(None) is None

    def test_serialize_list(self):
        import json

        result = JsonColumn().serialize([1, 2, 3])
        assert result is not None
        assert json.loads(result) == [1, 2, 3]

    def test_deserialize_dict(self):
        assert JsonColumn().deserialize("{\"key\": \"value\"}") == {"key": "value"}

    def test_deserialize_list(self):
        assert JsonColumn().deserialize("[1, 2, 3]") == [1, 2, 3]

    def test_deserialize_none_returns_none(self):
        assert JsonColumn().deserialize(None) is None

    def test_roundtrip_nested(self):
        col = JsonColumn()
        data = {"a": 1, "b": [1, 2], "c": {"d": True}}
        assert col.deserialize(col.serialize(data)) == data


class TestStringColumn:
    def test_pytype(self):
        assert StringColumn().pytype is str

    def test_serialize_passthrough(self):
        assert StringColumn().serialize("hello") == "hello"

    def test_deserialize_passthrough(self):
        assert StringColumn().deserialize("hello") == "hello"

    def test_deserialize_none_returns_none(self):
        assert StringColumn().deserialize(None) is None


class TestUuidColumn:
    def test_pytype(self):
        assert UuidColumn().pytype is uuid.UUID

    def test_has_default_factory(self):
        col = UuidColumn()
        assert callable(col.default)

    def test_default_generates_uuid(self):
        col = UuidColumn()
        assert callable(col.default)
        result = col.default()
        assert isinstance(result, uuid.UUID)

    def test_default_generates_unique_values(self):
        col = UuidColumn()
        assert callable(col.default)
        assert col.default() != col.default()

    def test_custom_default_not_overridden(self):
        fixed = uuid.UUID("00000000-0000-0000-0000-000000000000")
        col = UuidColumn(default=lambda: fixed)
        assert callable(col.default)
        assert col.default() == fixed

    def test_serialize(self):
        u = uuid.UUID("12345678-1234-5678-1234-567812345678")
        assert UuidColumn().serialize(u) == "12345678-1234-5678-1234-567812345678"

    def test_serialize_none_returns_none(self):
        assert UuidColumn().serialize(None) is None

    def test_deserialize(self):
        s = "12345678-1234-5678-1234-567812345678"
        assert UuidColumn().deserialize(s) == uuid.UUID(s)

    def test_deserialize_none_returns_none(self):
        assert UuidColumn().deserialize(None) is None

    def test_roundtrip(self):
        col = UuidColumn()
        u = uuid.uuid4()
        assert col.deserialize(col.serialize(u)) == u

    def test_equals_does_not_set_default(self):
        # UuidColumn with equals= used to crash because setdefault("default")
        # ran unconditionally, triggering the equals+default mutual exclusion.
        dep = IntColumn()
        col = UuidColumn(dep, equals=lambda x: uuid.UUID(int=x))
        assert col.default is None
        assert col.equals is not None

    def test_no_default_when_equals_provided(self):
        dep = IntColumn()
        col = UuidColumn(dep, equals=lambda x: uuid.UUID(int=x))
        assert col.default is None


class TestBytesColumn:
    def test_pytype(self):
        assert BytesColumn().pytype is bytes

    def test_serialize_returns_base64_string(self):
        import base64

        raw = b"hello world"
        result = BytesColumn().serialize(raw)
        assert isinstance(result, str)
        assert base64.b64decode(result) == raw

    def test_serialize_none_returns_none(self):
        assert BytesColumn().serialize(None) is None

    def test_deserialize_returns_bytes(self):
        col = BytesColumn()
        raw = b"\x00\xff\xab"
        assert col.deserialize(col.serialize(raw)) == raw

    def test_roundtrip_binary(self):
        col = BytesColumn()
        data = bytes(range(256))
        assert col.deserialize(col.serialize(data)) == data

    def test_roundtrip_empty(self):
        col = BytesColumn()
        assert col.deserialize(col.serialize(b"")) == b""

    def test_deserialize_none_returns_none(self):
        assert BytesColumn().deserialize(None) is None
