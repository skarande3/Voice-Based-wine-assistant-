from __future__ import annotations

from datetime import datetime, timezone
import logging
from threading import Lock

import httpx
import pandas as pd

from app.config import settings
from app.models import Catalog, DataSnapshot
from app.services.data_cleaner import build_catalog, clean_wine_dataframe

logger = logging.getLogger(__name__)


class DatasetStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._df = pd.DataFrame()
        self._catalog = Catalog()
        self._loaded_from = ""
        self._loaded_at = ""

    def load(self) -> DataSnapshot:
        with self._lock:
            raw_df, loaded_from = _load_raw_dataframe()
            cleaned_df = clean_wine_dataframe(raw_df)

            self._df = cleaned_df
            self._catalog = build_catalog(cleaned_df)
            self._loaded_from = loaded_from
            self._loaded_at = datetime.now(timezone.utc).isoformat()

            logger.info(
                "Loaded wine dataset: %s rows from %s",
                len(self._df),
                self._loaded_from,
            )

            return DataSnapshot(
                dataframe_columns=self._df.columns.tolist(),
                row_count=len(self._df),
                loaded_from=self._loaded_from,
                loaded_at=self._loaded_at,
            )

    def dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def catalog(self) -> Catalog:
        return self._catalog

    def metadata(self) -> dict[str, str | int]:
        return {
            "loaded_from": self._loaded_from,
            "loaded_at": self._loaded_at,
            "row_count": len(self._df),
        }

    def is_loaded(self) -> bool:
        return not self._df.empty


def _load_raw_dataframe() -> tuple[pd.DataFrame, str]:
    try:
        with httpx.Client(timeout=settings.request_timeout_seconds, follow_redirects=True) as client:
            response = client.get(settings.csv_export_url)
            response.raise_for_status()
        df = pd.read_csv(pd.io.common.StringIO(response.text))
        return df, settings.csv_export_url
    except Exception as exc:
        logger.warning("CSV fetch failed, trying local dataset fallback: %s", exc)

    if settings.local_dataset_path.exists():
        df = pd.read_excel(settings.local_dataset_path)
        return df, str(settings.local_dataset_path)

    raise RuntimeError(
        "Failed to load dataset from Google Sheets and no local fallback dataset was found."
    )


dataset_store = DatasetStore()
