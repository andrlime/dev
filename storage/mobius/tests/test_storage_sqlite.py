import pytest

from mobius import (
    Blueprint,
    BoolColumn,
    FloatColumn,
    IntColumn,
    Schema,
    SqliteBackend,
    StringColumn,
)


class _SampleBlueprint(Blueprint):
    def schema(self):
        self.name = StringColumn()
        self.age = IntColumn()
        self.active = BoolColumn()
        self.score = FloatColumn()


_SAMPLE_SCHEMA = Schema(_SampleBlueprint())


class TestSqliteSpecific:
    def test_persists_across_reconnect(self, tmp_path):
        path = tmp_path / "db.sqlite"
        db = SqliteBackend(_SAMPLE_SCHEMA, path, table="sample")
        db.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        db.close()

        db2 = SqliteBackend(_SAMPLE_SCHEMA, path, table="sample")
        rows = db2.read_all()
        db2.close()
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"

    def test_column_flags_in_ddl(self):
        class FlagBlueprint(Blueprint):
            def schema(self):
                self.id = IntColumn(primary_key=True, nullable=False)
                self.val = StringColumn(unique=True, indexed=True)

        schema = Schema(FlagBlueprint())
        db = SqliteBackend(schema, ":memory:", table="flags")
        db.insert({"id": 1, "val": "a"})
        assert db.read_all()[0]["id"] == 1
        db.close()

    def test_query_returns_rows(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        db.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        db.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        rows = db.query("SELECT \"name\", \"age\" FROM \"sample\" ORDER BY \"age\"")
        assert rows == [{"name": "Bob", "age": 25}, {"name": "Alice", "age": 30}]
        db.close()

    def test_query_with_params(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        db.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        db.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        rows = db.query("SELECT \"name\" FROM \"sample\" WHERE \"age\" > ?", (26,))
        assert rows == [{"name": "Alice"}]
        db.close()

    def test_query_empty_result(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        rows = db.query("SELECT * FROM \"sample\"")
        assert rows == []
        db.close()

    def test_query_ddl_returns_empty_list(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        result = db.query("CREATE TABLE IF NOT EXISTS \"tmp\" (x INTEGER)")
        assert result == []
        db.close()

    def test_query_aggregation(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        db.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        db.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        rows = db.query("SELECT COUNT(*) AS cnt FROM \"sample\"")
        assert rows[0]["cnt"] == 2
        db.close()

    def test_query_bad_sql_raises(self):
        db = SqliteBackend(_SAMPLE_SCHEMA, ":memory:", table="sample")
        with pytest.raises(Exception):
            db.query("SELECT * FROM nonexistent_table")
        db.close()

    def test_explicit_table_name_avoids_collision(self, tmp_path):
        path = tmp_path / "db.sqlite"

        class MyTable(Blueprint):
            def schema(self):
                self.x = IntColumn()

        class MyTable2(Blueprint):  # same class name, different schema
            def schema(self):
                self.label = StringColumn()

        s1 = Schema(MyTable())
        s2 = Schema(MyTable2())
        db1 = SqliteBackend(s1, path, table="table_a")
        db2 = SqliteBackend(s2, path, table="table_b")
        db1.insert({"x": 42})
        db2.insert({"label": "hello"})
        assert db1.read_all()[0]["x"] == 42
        assert db2.read_all()[0]["label"] == "hello"
        db1.close()
        db2.close()
