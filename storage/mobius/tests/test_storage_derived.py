class TestDerivedColumnsStored:
    def test_derived_column_persisted(self, derived_backend):
        derived_backend.add_row(x=3, y=4)
        rows = derived_backend.read_all()
        assert rows[0]["total"] == 7

    def test_derived_column_value_correct(self, derived_backend):
        derived_backend.add_row(x=10, y=20)
        assert derived_backend.read_all()[0]["total"] == 30
