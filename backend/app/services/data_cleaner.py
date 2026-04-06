from __future__ import annotations

import json
import logging
import re

import pandas as pd

from app.models import Catalog
from app.utils.text_utils import normalize_spaces, normalize_text

logger = logging.getLogger(__name__)

REQUIRED_SOURCE_COLUMNS = {
    "Id",
    "Name",
    "Producer",
    "Country",
    "Region",
    "Appellation",
    "Retail",
    "Varietal",
    "Vintage",
    "color",
    "ABV",
    "professional_ratings",
    "reference_url",
    "image_url",
    "volume_ml",
}

COLUMN_RENAME_MAP = {
    "Id": "id",
    "Name": "name",
    "Producer": "producer",
    "Country": "country",
    "Region": "region",
    "Appellation": "appellation",
    "Retail": "price",
    "Varietal": "varietal",
    "Vintage": "vintage",
    "color": "color",
    "ABV": "abv",
    "professional_ratings": "professional_ratings",
    "reference_url": "reference_url",
    "image_url": "image_url",
    "volume_ml": "volume_ml",
}


def clean_wine_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_SOURCE_COLUMNS.difference(raw_df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    df = raw_df.rename(columns=COLUMN_RENAME_MAP).copy()

    text_columns = ["name", "producer", "country", "region", "appellation", "varietal", "color", "reference_url", "image_url"]
    for column in text_columns:
        df[column] = df[column].fillna("").map(normalize_spaces)

    df["vintage"] = df["vintage"].fillna("").map(_clean_vintage)
    df["id"] = pd.to_numeric(df["id"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["abv"] = pd.to_numeric(df["abv"], errors="coerce")
    df["volume_ml"] = pd.to_numeric(df["volume_ml"], errors="coerce")

    ratings = df["professional_ratings"].fillna("").map(_parse_professional_ratings)
    df["ratings"] = ratings
    df["rating"] = ratings.map(_rating_average)
    df["rating_max"] = ratings.map(_rating_max)
    df["rating_count"] = ratings.map(len)
    df["summary_note"] = ratings.map(_primary_note)
    df["summary_note_normalized"] = df["summary_note"].fillna("").map(normalize_text)

    for column in ["name", "producer", "country", "region", "appellation", "varietal", "color"]:
        df[f"{column}_normalized"] = df[column].map(normalize_text)

    df["search_blob"] = df.apply(
        lambda row: " ".join(
            value
            for value in [
                row["name_normalized"],
                row["producer_normalized"],
                row["country_normalized"],
                row["region_normalized"],
                row["appellation_normalized"],
                row["varietal_normalized"],
                row["color_normalized"],
                row["summary_note_normalized"],
            ]
            if value
        ),
        axis=1,
    )

    return df


def build_catalog(df: pd.DataFrame) -> Catalog:
    return Catalog(
        countries=_sorted_unique(df["country"]),
        regions=_sorted_unique(df["region"]),
        appellations=_sorted_unique(df["appellation"]),
        varietals=_sorted_unique(df["varietal"]),
        colors=_sorted_unique(df["color"]),
    )


def _sorted_unique(series: pd.Series) -> list[str]:
    values = [normalize_spaces(value) for value in series.tolist() if normalize_spaces(value)]
    return sorted(set(values))


def _clean_vintage(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = normalize_spaces(str(value))
    if not text:
        return ""
    match = re.search(r"\d{4}", text)
    return match.group(0) if match else text


def _parse_professional_ratings(value: object) -> list[dict]:
    if value is None:
        return []

    text = normalize_spaces(str(value))
    if not text:
        return []

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Unable to decode professional_ratings JSON")
        return []

    results: list[dict] = []
    for item in parsed if isinstance(parsed, list) else []:
        if not isinstance(item, dict):
            continue
        score = item.get("score")
        max_score = item.get("max_score") or 100
        note = normalize_spaces(item.get("note") or "")
        source = normalize_spaces(item.get("source") or "")

        try:
            score_value = float(score)
            max_score_value = float(max_score)
        except (TypeError, ValueError):
            continue

        if max_score_value <= 0:
            continue

        normalized_score = round((score_value / max_score_value) * 100, 1)
        results.append(
            {
                "source": source,
                "score": normalized_score,
                "note": note,
            }
        )

    return results


def _rating_average(ratings: list[dict]) -> float | None:
    if not ratings:
        return None
    return round(sum(item["score"] for item in ratings) / len(ratings), 1)


def _rating_max(ratings: list[dict]) -> float | None:
    if not ratings:
        return None
    return max(item["score"] for item in ratings)


def _primary_note(ratings: list[dict]) -> str | None:
    for item in ratings:
        note = normalize_spaces(item.get("note"))
        if note:
            return note
    return None
