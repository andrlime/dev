from mobius import Blueprint


class TestBlueprintProtocol:
    def test_class_with_schema_method_satisfies_protocol(self):
        class MyBP:
            def schema(self) -> None:
                pass

        assert isinstance(MyBP(), Blueprint)

    def test_class_without_schema_method_fails(self):
        class NotABP:
            pass

        assert not isinstance(NotABP(), Blueprint)

    def test_schema_method_wrong_name_fails(self):
        class WrongName:
            def define(self) -> None:
                pass

        assert not isinstance(WrongName(), Blueprint)

    def test_concrete_subclass_satisfies_protocol(self):
        class ConcreteBP(Blueprint):
            def schema(self) -> None:
                pass

        assert isinstance(ConcreteBP(), Blueprint)
