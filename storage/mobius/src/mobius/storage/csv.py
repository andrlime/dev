import csv
from pathlib import Path

from mobius.column.column import Column, SQLiteValue
from mobius.schema import Schema
from mobius.storage.backend import StorageBackend

_NULL = r"\N"


def _from_csv_str(col: Column, val: str) -> SQLiteValue:
    if val == _NULL:
        return None
    if col.pytype is int or col.pytype is bool:
        return int(val)
    if col.pytype is float:
        return float(val)
    return val


class CsvBackend(StorageBackend):
    def __init__(self, schema: Schema, path: str | Path) -> None:
        super().__init__(schema)
        self._path = Path(path)
        self._names = list(schema.columns.keys())
        if not self._path.exists():
            with self._path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self._names)

    def insert(self, row: dict) -> None:
        values = [
            _NULL if (v := self.schema.columns[n].serialize(row[n])) is None else str(v)
            for n in self._names
        ]

        with self._path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(values)

    def read_all(self) -> list[dict]:
        rows = []
        with self._path.open(newline="", encoding="utf-8") as f:
            for raw in csv.DictReader(f):
                rows.append(
                    {
                        n: self.schema.columns[n].deserialize(
                            _from_csv_str(self.schema.columns[n], raw[n])
                        )
                        for n in self._names
                    }
                )
        return rows

    def delete_all(self) -> None:
        with self._path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(self._names)
