import uuid
from datetime import date, datetime

import pytest

from mobius import (
    Blueprint,
    BoolColumn,
    CsvBackend,
    DateColumn,
    DateTimeColumn,
    FloatColumn,
    IntColumn,
    JsonColumn,
    JsonlBackend,
    Schema,
    SqliteBackend,
    StringColumn,
    UuidColumn,
)


class SampleBlueprint(Blueprint):
    def schema(self):
        self.name = StringColumn()
        self.age = IntColumn()
        self.active = BoolColumn()
        self.score = FloatColumn()


class DerivedBlueprint(Blueprint):
    def schema(self):
        self.x = IntColumn()
        self.y = IntColumn()
        self.total = IntColumn(self.x, self.y, equals=lambda x, y: x + y)


class RichBlueprint(Blueprint):
    def schema(self):
        self.label = StringColumn()
        self.count = IntColumn()
        self.ratio = FloatColumn()
        self.flag = BoolColumn()
        self.uid = UuidColumn()
        self.day = DateColumn()
        self.ts = DateTimeColumn()
        self.meta = JsonColumn()


SAMPLE_SCHEMA = Schema(SampleBlueprint())
DERIVED_SCHEMA = Schema(DerivedBlueprint())
RICH_SCHEMA = Schema(RichBlueprint())

FIXED_UUID = uuid.UUID("12345678-1234-5678-1234-567812345678")
FIXED_DATE = date(2024, 3, 15)
FIXED_DT = datetime(2024, 3, 15, 12, 30, 0)


@pytest.fixture(params=["sqlite", "jsonl", "csv"])
def backend(request, tmp_path):
    if request.param == "sqlite":
        return SqliteBackend(SAMPLE_SCHEMA, ":memory:", table="sample")
    if request.param == "jsonl":
        return JsonlBackend(SAMPLE_SCHEMA, tmp_path / "data.jsonl")
    return CsvBackend(SAMPLE_SCHEMA, tmp_path / "data.csv")


@pytest.fixture(params=["sqlite", "jsonl", "csv"])
def derived_backend(request, tmp_path):
    if request.param == "sqlite":
        return SqliteBackend(DERIVED_SCHEMA, ":memory:", table="derived")
    if request.param == "jsonl":
        return JsonlBackend(DERIVED_SCHEMA, tmp_path / "data.jsonl")
    return CsvBackend(DERIVED_SCHEMA, tmp_path / "data.csv")


@pytest.fixture(params=["sqlite", "jsonl", "csv"])
def rich_backend(request, tmp_path):
    if request.param == "sqlite":
        return SqliteBackend(RICH_SCHEMA, ":memory:", table="rich")
    if request.param == "jsonl":
        return JsonlBackend(RICH_SCHEMA, tmp_path / "data.jsonl")
    return CsvBackend(RICH_SCHEMA, tmp_path / "data.csv")
