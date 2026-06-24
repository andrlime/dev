import uuid

import pytest

from mobius import Blueprint, IntColumn, StringColumn, Table, UuidColumn


def birth_year(age: int) -> int:
    return 2025 - age


def greeting(name: str, age: int) -> str:
    return f"Hi {name}, you are {age}"


class PersonBlueprint(Blueprint):
    def schema(self):
        self.name = StringColumn()
        self.age = IntColumn()
        self.birth_year = IntColumn(self.age, equals=birth_year)
        self.greeting = StringColumn(self.name, self.age, equals=greeting)


class TestTable:
    def test_add_row_returns_dict(self):
        table = Table(PersonBlueprint())
        row = table.add_row(name="Alice", age=30)
        assert isinstance(row, dict)

    def test_add_row_includes_roots(self):
        table = Table(PersonBlueprint())
        row = table.add_row(name="Alice", age=30)
        assert row["name"] == "Alice"
        assert row["age"] == 30

    def test_add_row_computes_derived(self):
        table = Table(PersonBlueprint())
        row = table.add_row(name="Alice", age=30)
        assert row["birth_year"] == 1995
        assert row["greeting"] == "Hi Alice, you are 30"

    def test_multi_dep_named_function(self):
        table = Table(PersonBlueprint())
        row = table.add_row(name="Bob", age=25)
        assert row["greeting"] == "Hi Bob, you are 25"

    def test_add_row_stores_row(self):
        table = Table(PersonBlueprint())
        table.add_row(name="Alice", age=30)
        assert len(table.all_rows()) == 1

    def test_all_rows_empty_initially(self):
        table = Table(PersonBlueprint())
        assert table.all_rows() == []

    def test_all_rows_accumulates(self):
        table = Table(PersonBlueprint())
        table.add_row(name="Alice", age=30)
        table.add_row(name="Bob", age=25)
        assert len(table.all_rows()) == 2

    def test_rows_are_independent(self):
        table = Table(PersonBlueprint())
        r1 = table.add_row(name="Alice", age=30)
        r2 = table.add_row(name="Bob", age=25)
        assert r1 is not r2
        assert r1["name"] != r2["name"]
        assert r1["birth_year"] != r2["birth_year"]

    def test_schema_name(self):
        table = Table(PersonBlueprint())
        assert table.schema.name == "PersonBlueprint"

    def test_add_row_unknown_column_raises(self):
        table = Table(PersonBlueprint())
        with pytest.raises(ValueError, match="unknown"):
            table.add_row(name="Alice", age=30, extra=99)

    def test_add_row_missing_column_raises(self):
        table = Table(PersonBlueprint())
        with pytest.raises(ValueError, match="missing"):
            table.add_row(name="Alice")

    def test_returned_row_is_stored_row(self):
        table = Table(PersonBlueprint())
        row = table.add_row(name="Alice", age=30)
        assert table.all_rows()[0] is row


class TestTableDefaults:
    def test_default_applied_when_omitted(self):
        class WithUuid(Blueprint):
            def schema(self):
                self.id = UuidColumn()
                self.name = StringColumn()

        table = Table(WithUuid())
        row = table.add_row(name="Alice")
        assert isinstance(row["id"], uuid.UUID)

    def test_default_generates_unique_values(self):
        class WithUuid(Blueprint):
            def schema(self):
                self.id = UuidColumn()
                self.name = StringColumn()

        table = Table(WithUuid())
        r1 = table.add_row(name="Alice")
        r2 = table.add_row(name="Bob")
        assert r1["id"] != r2["id"]

    def test_non_callable_default(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.status = StringColumn(default="active")
                self.name = StringColumn()

        table = Table(WithDefault())
        row = table.add_row(name="Alice")
        assert row["status"] == "active"

    def test_explicit_value_overrides_default(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.status = StringColumn(default="active")

        table = Table(WithDefault())
        row = table.add_row(status="inactive")
        assert row["status"] == "inactive"


class TestTableValidators:
    def test_validator_accepts_valid(self):
        class Validated(Blueprint):
            def schema(self):
                self.age = IntColumn(validator=lambda v: v >= 0)

        table = Table(Validated())
        row = table.add_row(age=25)
        assert row["age"] == 25

    def test_validator_rejects_invalid(self):
        class Validated(Blueprint):
            def schema(self):
                self.age = IntColumn(validator=lambda v: v >= 0)

        table = Table(Validated())
        with pytest.raises(ValueError, match="validation"):
            table.add_row(age=-1)

    def test_rejected_row_not_stored(self):
        class Validated(Blueprint):
            def schema(self):
                self.age = IntColumn(validator=lambda v: v >= 0)

        table = Table(Validated())
        with pytest.raises(ValueError):
            table.add_row(age=-1)
        assert table.all_rows() == []


class TestTableConstraints:
    def test_nullable_false_rejected(self):
        class Strict(Blueprint):
            def schema(self):
                self.x = IntColumn(nullable=False)

        table = Table(Strict())
        with pytest.raises(ValueError, match="nullable"):
            table.add_row(x=None)

    def test_nullable_false_row_not_stored(self):
        class Strict(Blueprint):
            def schema(self):
                self.x = IntColumn(nullable=False)

        table = Table(Strict())
        with pytest.raises(ValueError):
            table.add_row(x=None)
        assert table.all_rows() == []

    def test_unique_rejects_duplicate(self):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        table = Table(Uniq())
        table.add_row(email="a@b.com")
        with pytest.raises(ValueError, match="unique"):
            table.add_row(email="a@b.com")

    def test_unique_allows_different_values(self):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        table = Table(Uniq())
        table.add_row(email="a@b.com")
        table.add_row(email="c@d.com")
        assert len(table.all_rows()) == 2

    def test_unique_allows_multiple_nulls(self):
        class Uniq(Blueprint):
            def schema(self):
                self.email = StringColumn(unique=True)

        table = Table(Uniq())
        table.add_row(email=None)
        table.add_row(email=None)
        assert len(table.all_rows()) == 2
