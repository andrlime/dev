from mobius.column.column import Column


class FloatColumn(Column):
    def __init__(self, *deps: Column, **kwargs):
        super().__init__(*deps, **kwargs)
        self.pytype = float
