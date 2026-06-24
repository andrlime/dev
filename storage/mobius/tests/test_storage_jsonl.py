from mobius import (
    Blueprint,
    BoolColumn,
    FloatColumn,
    IntColumn,
    JsonlBackend,
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


class TestJsonlSpecific:
    def test_one_line_per_row(self, tmp_path):
        path = tmp_path / "data.jsonl"
        backend = JsonlBackend(_SAMPLE_SCHEMA, path)
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
        assert len(lines) == 2

    def test_appends_to_existing_file(self, tmp_path):
        path = tmp_path / "data.jsonl"
        b1 = JsonlBackend(_SAMPLE_SCHEMA, path)
        b1.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})

        b2 = JsonlBackend(_SAMPLE_SCHEMA, path)
        b2.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        assert len(b2.read_all()) == 2
