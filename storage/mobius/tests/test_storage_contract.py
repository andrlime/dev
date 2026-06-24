import pytest


class TestStorageContract:
    def test_read_all_empty(self, backend):
        assert backend.read_all() == []

    def test_insert_and_read_back(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        rows = backend.read_all()
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"
        assert rows[0]["age"] == 30
        assert rows[0]["active"] is True
        assert rows[0]["score"] == pytest.approx(9.5)

    def test_multiple_inserts_preserve_order(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        rows = backend.read_all()
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"

    def test_add_row_resolves_and_inserts(self, backend):
        row = backend.add_row(name="Carol", age=40, active=False, score=8.0)
        assert row["name"] == "Carol"
        assert backend.read_all()[0]["name"] == "Carol"

    def test_bool_false_roundtrip(self, backend):
        backend.insert({"name": "x", "age": 0, "active": False, "score": 0.0})
        assert backend.read_all()[0]["active"] is False

    def test_bool_true_roundtrip(self, backend):
        backend.insert({"name": "x", "age": 0, "active": True, "score": 0.0})
        assert backend.read_all()[0]["active"] is True

    def test_count_empty(self, backend):
        assert backend.count() == 0

    def test_count_after_inserts(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        assert backend.count() == 2

    def test_delete_all_clears_rows(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.delete_all()
        assert backend.read_all() == []

    def test_delete_all_resets_count(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.delete_all()
        assert backend.count() == 0

    def test_insert_after_delete_all(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.delete_all()
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        rows = backend.read_all()
        assert len(rows) == 1
        assert rows[0]["name"] == "Bob"

    def test_find_by_single_field(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        results = backend.find(name="Alice")
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_find_by_multiple_fields(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Alice", "age": 25, "active": False, "score": 7.0})
        results = backend.find(name="Alice", age=30)
        assert len(results) == 1
        assert results[0]["age"] == 30

    def test_find_no_match(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        assert backend.find(name="Nobody") == []

    def test_find_multiple_matches(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Alice", "age": 40, "active": True, "score": 8.0})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        results = backend.find(name="Alice")
        assert len(results) == 2

    def test_find_empty_kwargs_returns_all(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        assert len(backend.find()) == 2

    def test_find_by_bool_true(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        results = backend.find(active=True)
        assert len(results) == 1
        assert results[0]["name"] == "Alice"

    def test_find_by_bool_false(self, backend):
        backend.insert({"name": "Alice", "age": 30, "active": True, "score": 9.5})
        backend.insert({"name": "Bob", "age": 25, "active": False, "score": 7.0})
        results = backend.find(active=False)
        assert len(results) == 1
        assert results[0]["name"] == "Bob"
