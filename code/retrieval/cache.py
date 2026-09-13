from __future__ import annotations

from pathlib import Path
from threading import Lock

import polars as pl


class DatasetCache:
    """
    Thread-safe Singleton cache.

    Features
    --------
    • Lazy loading
    • Read each CSV only once
    • Shared across the entire application
    """

    _instance: DatasetCache | None = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._data = {}
        return cls._instance

    def get_dataframe(self, path: Path) -> pl.DataFrame:
        key = str(path.resolve())

        if key not in self._data:
            self._data[key] = pl.read_csv(
                path,
                try_parse_dates=True
            )

        return self._data[key]

    def clear(self):
        self._data.clear()

    @property
    def loaded_files(self):
        return list(self._data.keys())