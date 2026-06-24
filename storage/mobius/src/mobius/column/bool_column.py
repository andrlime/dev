from mobius.column.column import Column


class BoolColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = bool

    def serialize(self, value: bool | None) -> int | None:
        if value is None:
            return None
        return 1 if value else 0
