import uuid
from datetime import date, datetime

import pytest

FIXED_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")
FIXED_DATE = date(2024, 3, 15)
FIXED_DT = datetime(2024, 3, 15, 12, 30, 0)

RICH_ROW = {
    "label": "test",
    "count": 42,
    "ratio": 3.14,
    "flag": True,
    "uid": FIXED_UUID,
    "day": FIXED_DATE,
    "ts": FIXED_DT,
    "meta": {"key": "value", "nums": [1, 2, 3]},
}


class TestRichTypeRoundtrips:
    def test_string_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["label"] == "test"

    def test_int_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["count"] == 42

    def test_float_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["ratio"] == pytest.approx(3.14)

    def test_bool_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["flag"] is True

    def test_uuid_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["uid"] == FIXED_UUID

    def test_date_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["day"] == FIXED_DATE

    def test_datetime_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["ts"] == FIXED_DT

    def test_json_roundtrip(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        assert rich_backend.read_all()[0]["meta"] == RICH_ROW["meta"]

    def test_find_by_uuid(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        results = rich_backend.find(uid=FIXED_UUID)
        assert len(results) == 1
        assert results[0]["uid"] == FIXED_UUID

    def test_find_by_date(self, rich_backend):
        rich_backend.insert(RICH_ROW)
        results = rich_backend.find(day=FIXED_DATE)
        assert len(results) == 1
        assert results[0]["day"] == FIXED_DATE


class TestNullableTypedColumns:
    def test_null_date_roundtrip(self, rich_backend):
        row: dict = dict(RICH_ROW)
        row["day"] = None
        rich_backend.insert(row)
        assert rich_backend.read_all()[0]["day"] is None

    def test_null_datetime_roundtrip(self, rich_backend):
        row: dict = dict(RICH_ROW)
        row["ts"] = None
        rich_backend.insert(row)
        assert rich_backend.read_all()[0]["ts"] is None

    def test_null_uuid_roundtrip(self, rich_backend):
        row: dict = dict(RICH_ROW)
        row["uid"] = None
        rich_backend.insert(row)
        assert rich_backend.read_all()[0]["uid"] is None

    def test_null_json_roundtrip(self, rich_backend):
        row: dict = dict(RICH_ROW)
        row["meta"] = None
        rich_backend.insert(row)
        assert rich_backend.read_all()[0]["meta"] is None
