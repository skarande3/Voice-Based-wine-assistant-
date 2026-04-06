from __future__ import annotations

import pandas as pd


def gift_recommendations(df: pd.DataFrame, limit: int) -> pd.DataFrame:
    working = df.copy()

    if working.empty:
        return working

    # This is intentionally transparent and conservative:
    # 1. Prefer bottles with critic ratings.
    # 2. Prefer a gift-friendly price band.
    # 3. Prefer recognizable styles and regions when available.
    working["gift_score"] = 0.0
    working.loc[working["rating"].notna(), "gift_score"] += working["rating"].fillna(0) / 10
    working.loc[working["price"].between(30, 90, inclusive="both"), "gift_score"] += 4
    working.loc[working["price"].between(20, 120, inclusive="both"), "gift_score"] += 1
    working.loc[
        working["color_normalized"].isin(["sparkling", "red", "white"]),
        "gift_score",
    ] += 1
    working.loc[
        working["country_normalized"].isin(["france", "italy", "united states"]),
        "gift_score",
    ] += 0.5

    return (
        working.sort_values(
            by=["gift_score", "rating", "price"],
            ascending=[False, False, False],
            na_position="last",
        )
        .head(limit)
        .copy()
    )
