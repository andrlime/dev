import pytest

from mobius import (
    Blueprint,
    BytesColumn,
    CsvBackend,
    IntColumn,
    JsonlBackend,
    Schema,
    SqliteBackend,
    StringColumn,
)


def _make_backend(backend_type, schema, tmp_path):
    if backend_type == "sqlite":
        return SqliteBackend(schema, ":memory:", table="test")
    if backend_type == "jsonl":
        return JsonlBackend(schema, tmp_path / "data.jsonl")
    return CsvBackend(schema, tmp_path / "data.csv")


class TestNullableConstraint:
    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_nullable_false_rejected_in_add_row(self, backend_type, tmp_path):
        class Strict(Blueprint):
            def schema(self):
                self.x = IntColumn(nullable=False)

        b = _make_backend(backend_type, Schema(Strict()), tmp_path)
        with pytest.raises(ValueError, match="nullable"):
            b.add_row(x=None)

    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_nullable_true_accepts_none(self, backend_type, tmp_path):
        class Lenient(Blueprint):
            def schema(self):
                self.x = IntColumn(nullable=True)

        b = _make_backend(backend_type, Schema(Lenient()), tmp_path)
        b.add_row(x=None)
        assert b.read_all()[0]["x"] is None


class TestUniqueConstraint:
    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_unique_rejects_duplicate_in_add_row(self, backend_type, tmp_path):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        b = _make_backend(backend_type, Schema(Uniq()), tmp_path)
        b.add_row(email="a@b.com")
        with pytest.raises((ValueError, Exception), match="unique|UNIQUE"):
            b.add_row(email="a@b.com")

    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_unique_allows_different_values(self, backend_type, tmp_path):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        b = _make_backend(backend_type, Schema(Uniq()), tmp_path)
        b.add_row(email="a@b.com")
        b.add_row(email="c@d.com")
        assert b.count() == 2

    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_unique_allows_multiple_nulls(self, backend_type, tmp_path):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        b = _make_backend(backend_type, Schema(Uniq()), tmp_path)
        b.add_row(email=None)
        b.add_row(email=None)
        assert b.count() == 2


class TestBytesBackend:
    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_bytes_roundtrip(self, backend_type, tmp_path):
        class WithBytes(Blueprint):
            def schema(self):
                self.data = BytesColumn()

        b = _make_backend(backend_type, Schema(WithBytes()), tmp_path)
        b.insert({"data": b"\x00\xff\xab"})
        assert b.read_all()[0]["data"] == b"\x00\xff\xab"

    @pytest.mark.parametrize("backend_type", ["sqlite", "jsonl", "csv"])
    def test_bytes_empty(self, backend_type, tmp_path):
        class WithBytes(Blueprint):
            def schema(self):
                self.data = BytesColumn()

        b = _make_backend(backend_type, Schema(WithBytes()), tmp_path)
        b.insert({"data": b""})
        assert b.read_all()[0]["data"] == b""
