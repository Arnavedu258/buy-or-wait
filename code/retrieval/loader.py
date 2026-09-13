from pathlib import Path
import polars as pl

from .cache import DatasetCache
from .logger import logger


class DatasetLoader:

    REQUIRED_FILES = [
        "financial_profiles.csv",
        "requests.csv",
        "financial_events.csv",
        "messages.csv",
        "images.csv",
        "request_payment_options.csv",
        "exchange_rates.csv",
    ]

    def __init__(self):

        self.root = (
            Path(__file__).resolve().parents[2] / "dataset"
        )

        self.cache = DatasetCache()

    def validate(self):

        missing = []

        for file in self.REQUIRED_FILES:
            if not (self.root / file).exists():
                missing.append(file)

        if missing:
            raise FileNotFoundError(
                f"Missing datasets: {missing}"
            )

        logger.info("Dataset validation passed")

    def load(self, filename: str) -> pl.DataFrame:

        path = self.root / filename

        logger.info(f"Reading {filename}")

        return self.cache.dataframe(path)