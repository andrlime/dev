import json
from pathlib import Path

from mobius.schema import Schema
from mobius.storage.backend import StorageBackend


class JsonlBackend(StorageBackend):
    def __init__(self, schema: Schema, path: str | Path) -> None:
        super().__init__(schema)
        self._path = Path(path)
        self._path.touch()

    def insert(self, row: dict) -> None:
        serialized = {
            n: col.serialize(row[n]) for n, col in self.schema.columns.items()
        }
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(serialized) + "\n")

    def read_all(self) -> list[dict]:
        rows = []
        with self._path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                raw = json.loads(line)
                rows.append(
                    {
                        n: col.deserialize(raw[n])
                        for n, col in self.schema.columns.items()
                    }
                )
        return rows

    def delete_all(self) -> None:
        self._path.write_text("", encoding="utf-8")
