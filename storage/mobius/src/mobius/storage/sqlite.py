import sqlite3
from pathlib import Path

from mobius.column.column import Column
from mobius.schema import Schema
from mobius.storage.backend import StorageBackend


def _affinity(col: Column) -> str:
    if col.pytype is bool or col.pytype is int:
        return "INTEGER"
    if col.pytype is float:
        return "REAL"
    return "TEXT"


class SqliteBackend(StorageBackend):
    def __init__(self, schema: Schema, path: str | Path, table: str) -> None:
        super().__init__(schema)
        self._conn = sqlite3.connect(str(path))
        self._table = table
        self._names = list(schema.columns.keys())
        self._create_table()

    def _create_table(self) -> None:
        col_defs = []
        for name, col in self.schema.columns.items():
            parts = [f"\"{name}\"", _affinity(col)]
            if col.primary_key:
                parts.append("PRIMARY KEY")
            if not col.nullable:
                parts.append("NOT NULL")
            if col.unique:
                parts.append("UNIQUE")
            col_defs.append(" ".join(parts))

        self._conn.execute(
            f"CREATE TABLE IF NOT EXISTS \"{self._table}\" ({", ".join(col_defs)})"
        )
        for name, col in self.schema.columns.items():
            if col.indexed:
                self._conn.execute(
                    f"CREATE INDEX IF NOT EXISTS \"idx_{self._table}_{name}\" "
                    f"ON \"{self._table}\" (\"{name}\")"
                )
        self._conn.commit()

    def _cols_clause(self) -> str:
        return ", ".join(f"\"{n}\"" for n in self._names)

    def _deserialize_row(self, raw: tuple) -> dict:
        return {
            n: self.schema.columns[n].deserialize(v) for n, v in zip(self._names, raw)
        }

    def insert(self, row: dict) -> None:
        values = [self.schema.columns[n].serialize(row[n]) for n in self._names]
        placeholders = ", ".join("?" * len(self._names))
        self._conn.execute(
            f"INSERT INTO \"{self._table}\" ({self._cols_clause()}) VALUES ({placeholders})",
            values,
        )
        self._conn.commit()

    def read_all(self) -> list[dict]:
        cursor = self._conn.execute(
            f"SELECT {self._cols_clause()} FROM \"{self._table}\" ORDER BY rowid"
        )
        return [self._deserialize_row(row) for row in cursor.fetchall()]

    def delete_all(self) -> None:
        self._conn.execute(f"DELETE FROM \"{self._table}\"")
        self._conn.commit()

    def count(self) -> int:
        cursor = self._conn.execute(f"SELECT COUNT(*) FROM \"{self._table}\"")
        return cursor.fetchone()[0]

    def find(self, **kwargs) -> list[dict]:
        if not kwargs:
            return self.read_all()
        where = " AND ".join(f"\"{n}\" = ?" for n in kwargs)
        values = [self.schema.columns[n].serialize(v) for n, v in kwargs.items()]
        cursor = self._conn.execute(
            f"SELECT {self._cols_clause()} FROM \"{self._table}\" WHERE {where} ORDER BY rowid",
            values,
        )
        return [self._deserialize_row(row) for row in cursor.fetchall()]

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        # The caller is responsible for preventing SQL injection attacks.
        cursor = self._conn.execute(sql, params)
        cols = [d[0] for d in cursor.description] if cursor.description else []
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def close(self) -> None:
        self._conn.close()
