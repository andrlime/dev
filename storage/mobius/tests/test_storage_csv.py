from mobius import (
    Blueprint,
    BoolColumn,
    CsvBackend,
    FloatColumn,
    IntColumn,
    Schema,
    StringColumn,
)


class _SampleBlueprint(Blueprint):
    def schema(self):
        self.name = StringColumn()
        self.age = IntColumn()
        self.active = BoolColumn()
        self.score = FloatColumn()


_SAMPLE_SCHEMA = Schema(_SampleBlueprint())


class TestCsvSpecific:
    def test_header_row_written(self, tmp_path):
        path = tmp_path / "data.csv"
        CsvBackend(_SAMPLE_SCHEMA, path)
        header = path.read_text().splitlines()[0]
        assert header == "name,age,active,score"

    def test_appends_to_existing_file(self, tmp_path):
        path = tmp_path / "data.csv"
        b1 = CsvBackend(_SAMPLE_SCHEMA, path)
        b1.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})

        b2 = CsvBackend(_SAMPLE_SCHEMA, path)
        b2.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        assert len(b2.read_all()) == 2

    def test_no_duplicate_header_on_reopen(self, tmp_path):
        path = tmp_path / "data.csv"
        CsvBackend(_SAMPLE_SCHEMA, path)
        CsvBackend(_SAMPLE_SCHEMA, path)
        lines = path.read_text().splitlines()
        assert lines[0] == "name,age,active,score"
        assert len([ln for ln in lines if ln == "name,age,active,score"]) == 1

    def test_empty_string_roundtrips_as_empty(self, tmp_path):
        path = tmp_path / "data.csv"
        b = CsvBackend(_SAMPLE_SCHEMA, path)
        b.insert({"name": "", "age": 0, "active": False, "score": 0.0})
        assert b.read_all()[0]["name"] == ""

    def test_none_roundtrips_as_none(self, tmp_path):
        path = tmp_path / "data.csv"
        b = CsvBackend(_SAMPLE_SCHEMA, path)
        b.insert({"name": None, "age": 0, "active": False, "score": 0.0})
        assert b.read_all()[0]["name"] is None
