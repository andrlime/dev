import pytest

from mobius import Blueprint, IntColumn, Schema, StringColumn, UuidColumn


class SimpleBlueprint(Blueprint):
    def schema(self):
        self.x = IntColumn()
        self.y = IntColumn()


def _sum(x: int, y: int) -> int:
    return x + y


class DerivedBlueprint(Blueprint):
    def schema(self):
        self.x = IntColumn()
        self.y = IntColumn()
        self.z = IntColumn(self.x, self.y, equals=_sum)


class TestSchemaInit:
    def test_name_from_source_class(self):
        assert Schema(SimpleBlueprint()).name == "SimpleBlueprint"

    def test_columns_collected(self):
        schema = Schema(SimpleBlueprint())
        assert set(schema.columns.keys()) == {"x", "y"}

    def test_column_names_assigned_from_attribute(self):
        schema = Schema(SimpleBlueprint())
        assert schema.columns["x"].name == "x"
        assert schema.columns["y"].name == "y"

    def test_roots_are_columns_without_deps_or_equals(self):
        schema = Schema(SimpleBlueprint())
        assert schema.roots == {"x", "y"}

    def test_derived_column_not_in_roots(self):
        schema = Schema(DerivedBlueprint())
        assert "z" not in schema.roots
        assert schema.roots == {"x", "y"}

    def test_topo_order_contains_all_columns(self):
        schema = Schema(DerivedBlueprint())
        assert set(schema.topo_order) == {"x", "y", "z"}

    def test_topo_order_deps_before_dependents(self):
        schema = Schema(DerivedBlueprint())
        assert schema.topo_order.index("x") < schema.topo_order.index("z")
        assert schema.topo_order.index("y") < schema.topo_order.index("z")

    def test_topo_order_chained(self):
        class ChainBlueprint(Blueprint):
            def schema(self):
                self.a = IntColumn()
                self.b = IntColumn(self.a, equals=lambda x: x * 2)
                self.c = IntColumn(self.b, equals=lambda x: x + 1)

        schema = Schema(ChainBlueprint())
        order = schema.topo_order
        assert order.index("a") < order.index("b")
        assert order.index("b") < order.index("c")

    def test_column_with_equals_not_in_roots(self):
        class EqualsOnlyBlueprint(Blueprint):
            def schema(self):
                self.a = IntColumn()
                self.b = IntColumn(self.a, equals=lambda x: x)

        schema = Schema(EqualsOnlyBlueprint())
        assert schema.roots == {"a"}

    def test_duplicate_column_object_raises(self):
        class DupBlueprint(Blueprint):
            def schema(self):
                col = IntColumn()
                self.a = col
                self.b = col

        with pytest.raises(ValueError, match="identically named"):
            Schema(DupBlueprint())

    def test_unregistered_dep_raises(self):
        class BadDepBlueprint(Blueprint):
            def schema(self):
                orphan = IntColumn()
                self.x = IntColumn(orphan, equals=lambda v: v)

        with pytest.raises(ValueError, match="unregistered"):
            Schema(BadDepBlueprint())

    def test_cycle_raises(self):
        class CyclicBlueprint(Blueprint):
            def schema(self):
                self.a = IntColumn()
                self.b = IntColumn(self.a, equals=lambda x: x)
                self.a.deps = (self.b,)
                self.a.equals = lambda x: x  # needed so a passes deps-without-equals

        with pytest.raises(ValueError, match="cycle"):
            Schema(CyclicBlueprint())

    def test_non_column_attributes_ignored(self):
        class MixedBlueprint(Blueprint):
            def schema(self):
                self.x = IntColumn()
                self.label = "not a column"
                self.count = 42

        schema = Schema(MixedBlueprint())
        assert set(schema.columns.keys()) == {"x"}


def double(x: int) -> int:
    return x * 2


def add(x: int, y: int) -> int:
    return x + y


def full_name(first: str, last: str) -> str:
    return f"{first} {last}"


def tax(subtotal: int, rate: int) -> int:
    return subtotal * rate // 100


def total(subtotal: int, tax_amount: int) -> int:
    return subtotal + tax_amount


class OrderBlueprint(Blueprint):
    def schema(self):
        self.subtotal = IntColumn()
        self.rate = IntColumn()
        self.tax_amount = IntColumn(self.subtotal, self.rate, equals=tax)
        self.total = IntColumn(self.subtotal, self.tax_amount, equals=total)


class TestSchemaResolve:
    def test_roots_pass_through(self):
        schema = Schema(SimpleBlueprint())
        result = schema.resolve(x=1, y=2)
        assert result["x"] == 1
        assert result["y"] == 2

    def test_derived_column_computed(self):
        schema = Schema(DerivedBlueprint())
        result = schema.resolve(x=3, y=4)
        assert result["z"] == 7

    def test_all_columns_in_result(self):
        schema = Schema(DerivedBlueprint())
        result = schema.resolve(x=1, y=2)
        assert set(result.keys()) == {"x", "y", "z"}

    def test_chained_derivation(self):
        class ChainBlueprint(Blueprint):
            def schema(self):
                self.a = IntColumn()
                self.b = IntColumn(self.a, equals=lambda x: x * 2)
                self.c = IntColumn(self.b, equals=lambda x: x + 1)

        schema = Schema(ChainBlueprint())
        result = schema.resolve(a=5)
        assert result["b"] == 10
        assert result["c"] == 11

    def test_unknown_kwarg_raises(self):
        schema = Schema(SimpleBlueprint())
        with pytest.raises(ValueError, match="unknown"):
            schema.resolve(x=1, y=2, z=99)

    def test_missing_kwarg_raises(self):
        schema = Schema(SimpleBlueprint())
        with pytest.raises(ValueError, match="missing"):
            schema.resolve(x=1)

    def test_derived_column_as_kwarg_raises(self):
        schema = Schema(DerivedBlueprint())
        with pytest.raises(ValueError, match="unknown"):
            schema.resolve(x=1, y=2, z=99)

    def test_multi_dep_derivation(self):
        class MultiBlueprint(Blueprint):
            def schema(self):
                self.a = StringColumn()
                self.b = StringColumn()
                self.c = StringColumn(self.a, self.b, equals=lambda x, y: f"{x} {y}")

        schema = Schema(MultiBlueprint())
        result = schema.resolve(a="hello", b="world")
        assert result["c"] == "hello world"

    def test_multi_level_named_functions(self):
        schema = Schema(OrderBlueprint())
        result = schema.resolve(subtotal=100, rate=8)
        assert result["tax_amount"] == 8
        assert result["total"] == 108

    def test_named_function_single_dep(self):
        class DoubleBlueprint(Blueprint):
            def schema(self):
                self.n = IntColumn()
                self.doubled = IntColumn(self.n, equals=double)

        schema = Schema(DoubleBlueprint())
        result = schema.resolve(n=7)
        assert result["doubled"] == 14

    def test_named_function_multi_dep(self):
        class AddBlueprint(Blueprint):
            def schema(self):
                self.x = IntColumn()
                self.y = IntColumn()
                self.total = IntColumn(self.x, self.y, equals=add)

        schema = Schema(AddBlueprint())
        result = schema.resolve(x=10, y=3)
        assert result["total"] == 13

    def test_named_function_string_dep(self):
        class NameBlueprint(Blueprint):
            def schema(self):
                self.first = StringColumn()
                self.last = StringColumn()
                self.name = StringColumn(self.first, self.last, equals=full_name)

        schema = Schema(NameBlueprint())
        result = schema.resolve(first="Jane", last="Doe")
        assert result["name"] == "Jane Doe"

    def test_empty_schema(self):
        class EmptyBlueprint(Blueprint):
            def schema(self):
                pass

        schema = Schema(EmptyBlueprint())
        assert schema.columns == {}
        assert schema.roots == set()
        assert schema.topo_order == []
        assert schema.resolve() == {}

    def test_constant_column_zero_deps(self):
        # A column with equals but no deps acts as a constant injected at resolve time.
        class ConstBlueprint(Blueprint):
            def schema(self):
                self.multiplier = IntColumn(equals=lambda: 10)
                self.x = IntColumn()
                self.result = IntColumn(
                    self.x, self.multiplier, equals=lambda x, m: x * m
                )

        schema = Schema(ConstBlueprint())
        assert "multiplier" not in schema.roots
        result = schema.resolve(x=5)
        assert result["multiplier"] == 10
        assert result["result"] == 50

    def test_diamond_dependency_topo_order(self):
        # shared appears exactly once; both mid_a and mid_b come after it; leaf comes last
        class DiamondBlueprint(Blueprint):
            def schema(self):
                self.shared = IntColumn()
                self.mid_a = IntColumn(self.shared, equals=lambda x: x + 1)
                self.mid_b = IntColumn(self.shared, equals=lambda x: x * 2)
                self.leaf = IntColumn(self.mid_a, self.mid_b, equals=lambda a, b: a + b)

        schema = Schema(DiamondBlueprint())
        order = schema.topo_order
        assert order.count("shared") == 1
        assert order.index("shared") < order.index("mid_a")
        assert order.index("shared") < order.index("mid_b")
        assert order.index("mid_a") < order.index("leaf")
        assert order.index("mid_b") < order.index("leaf")

    def test_diamond_dependency_resolve(self):
        class DiamondBlueprint(Blueprint):
            def schema(self):
                self.shared = IntColumn()
                self.mid_a = IntColumn(self.shared, equals=lambda x: x + 1)
                self.mid_b = IntColumn(self.shared, equals=lambda x: x * 2)
                self.leaf = IntColumn(self.mid_a, self.mid_b, equals=lambda a, b: a + b)

        schema = Schema(DiamondBlueprint())
        result = schema.resolve(shared=3)
        assert result["mid_a"] == 4  # 3 + 1
        assert result["mid_b"] == 6  # 3 * 2
        assert result["leaf"] == 10  # 4 + 6

    def test_resolve_idempotent(self):
        schema = Schema(DerivedBlueprint())
        assert schema.resolve(x=2, y=3) == schema.resolve(x=2, y=3)

    def test_complex_topology(self):
        # DAG:  a ──► c ──────────► f
        #        \                  ▲
        #         ──► d ──► e ──────┘
        #        /    ▲
        #       b ────┘
        #        \
        #         ──► g
        def c_fn(a: int) -> int:
            return a * 2

        def d_fn(a: int, b: int) -> int:
            return a + b

        def e_fn(d: int) -> int:
            return d - 1

        def f_fn(c: int, e: int) -> int:
            return c + e

        def g_fn(b: int) -> int:
            return b * 3

        class ComplexBlueprint(Blueprint):
            def schema(self):
                self.a = IntColumn()
                self.b = IntColumn()
                self.c = IntColumn(self.a, equals=c_fn)
                self.d = IntColumn(self.a, self.b, equals=d_fn)
                self.e = IntColumn(self.d, equals=e_fn)
                self.f = IntColumn(self.c, self.e, equals=f_fn)
                self.g = IntColumn(self.b, equals=g_fn)

        schema = Schema(ComplexBlueprint())
        assert schema.roots == {"a", "b"}

        order = schema.topo_order
        assert order.index("a") < order.index("c")
        assert order.index("a") < order.index("d")
        assert order.index("b") < order.index("d")
        assert order.index("b") < order.index("g")
        assert order.index("d") < order.index("e")
        assert order.index("c") < order.index("f")
        assert order.index("e") < order.index("f")

        result = schema.resolve(a=4, b=3)
        assert result["c"] == 8  # 4 * 2
        assert result["d"] == 7  # 4 + 3
        assert result["e"] == 6  # 7 - 1
        assert result["f"] == 14  # 8 + 6
        assert result["g"] == 9  # 3 * 3


class TestDepsWithoutEquals:
    def test_deps_without_equals_raises(self):
        class Bad(Blueprint):
            def schema(self):
                self.x = IntColumn()
                self.y = IntColumn(self.x)

        with pytest.raises(ValueError, match="equals"):
            Schema(Bad())


class TestDefaults:
    def test_default_applied_when_omitted(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.x = IntColumn(default=42)
                self.y = StringColumn()

        schema = Schema(WithDefault())
        result = schema.resolve(y="hello")
        assert result["x"] == 42
        assert result["y"] == "hello"

    def test_default_callable_called_each_time(self):
        import uuid

        class WithCallable(Blueprint):
            def schema(self):
                self.uid = UuidColumn()
                self.name = StringColumn()

        schema = Schema(WithCallable())
        r1 = schema.resolve(name="Alice")
        r2 = schema.resolve(name="Bob")
        assert isinstance(r1["uid"], uuid.UUID)
        assert r1["uid"] != r2["uid"]

    def test_explicit_value_overrides_default(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.x = IntColumn(default=42)

        schema = Schema(WithDefault())
        assert schema.resolve(x=99)["x"] == 99

    def test_default_column_not_in_required_roots(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.x = IntColumn(default=0)
                self.y = IntColumn()

        schema = Schema(WithDefault())
        with pytest.raises(ValueError, match="missing"):
            schema.resolve()  # y is required, x has a default

    def test_non_callable_default(self):
        class WithDefault(Blueprint):
            def schema(self):
                self.tag = StringColumn(default="unset")

        schema = Schema(WithDefault())
        assert schema.resolve()["tag"] == "unset"


class TestValidators:
    def test_validator_passes_valid_value(self):
        class Validated(Blueprint):
            def schema(self):
                self.age = IntColumn(validator=lambda v: v >= 0)

        result = Schema(Validated()).resolve(age=25)
        assert result["age"] == 25

    def test_validator_rejects_invalid_value(self):
        class Validated(Blueprint):
            def schema(self):
                self.age = IntColumn(validator=lambda v: v >= 0)

        with pytest.raises(ValueError, match="validation"):
            Schema(Validated()).resolve(age=-1)

    def test_validator_skipped_for_none(self):
        class Validated(Blueprint):
            def schema(self):
                self.x = IntColumn(validator=lambda v: v > 0)

        result = Schema(Validated()).resolve(x=None)
        assert result["x"] is None

    def test_validator_on_derived_column(self):
        class Validated(Blueprint):
            def schema(self):
                self.x = IntColumn()
                self.doubled = IntColumn(
                    self.x, equals=lambda v: v * 2, validator=lambda v: v < 100
                )

        schema = Schema(Validated())
        with pytest.raises(ValueError, match="validation"):
            schema.resolve(x=60)  # doubled=120 fails

    def test_named_function_validator(self):
        def non_negative(v: int) -> bool:
            return v >= 0

        class Validated(Blueprint):
            def schema(self):
                self.score = IntColumn(validator=non_negative)

        with pytest.raises(ValueError, match="validation"):
            Schema(Validated()).resolve(score=-5)
