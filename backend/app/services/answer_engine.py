from __future__ import annotations

import pandas as pd

from app.config import settings
from app.models import ParsedQuery
from app.schemas import AskResponse, ResponseMeta, WineResult
from app.services.recommendation_engine import gift_recommendations


def answer_question(
    question: str,
    parsed: ParsedQuery,
    df: pd.DataFrame,
    *,
    loaded_from: str,
) -> AskResponse:
    if parsed.intent == "ambiguous":
        suggested_results = _suggest_for_ambiguous_query(df, parsed)
        answer_text = parsed.clarification_message or "I need a bit more detail to answer that reliably."
        if suggested_results:
            answer_text = (
                f"{answer_text} Meanwhile, here are a few plausible matches from the dataset based on the keywords I found."
            )
        return _response(
            question=question,
            parsed=parsed,
            answer_text=answer_text,
            results=suggested_results,
            loaded_from=loaded_from,
            clarification_needed=True,
            reason="ambiguous_question",
        )

    if parsed.intent == "unsupported":
        return _response(
            question=question,
            parsed=parsed,
            answer_text=(
                parsed.unsupported_reason
                or "I can only answer questions grounded in the dataset's price, rating, region, country, varietal, and similar fields."
            ),
            results=[],
            loaded_from=loaded_from,
            unsupported=True,
            reason="unsupported_question",
        )

    result_df = _apply_filters(df, parsed)
    limit = settings.default_result_limit

    if parsed.intent == "most_expensive":
        result_df = result_df.sort_values(by=["price", "rating"], ascending=[False, False], na_position="last").head(limit)
    elif parsed.intent == "best_rated_under_price":
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    elif parsed.intent == "region_filter":
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    elif parsed.intent == "country_filter":
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    elif parsed.intent == "price_filter":
        result_df = result_df.sort_values(by=["price", "rating"], ascending=[True, False], na_position="last").head(limit)
    elif parsed.intent == "rating_filter":
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    elif parsed.intent == "color_filter":
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    elif parsed.intent == "recommendation_gift":
        result_df = gift_recommendations(result_df, limit)
    else:
        result_df = result_df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)

    if result_df.empty:
        return _response(
            question=question,
            parsed=parsed,
            answer_text="I could not find any wines in the dataset that match that request.",
            results=[],
            loaded_from=loaded_from,
            reason="no_results",
        )

    if parsed.intent == "most_expensive":
        answer_text = _build_most_expensive_text(result_df)
    elif parsed.intent == "best_rated_under_price":
        answer_text = _build_best_under_price_text(parsed, result_df)
    elif parsed.intent == "region_filter":
        answer_text = _build_region_text(parsed, result_df)
    elif parsed.intent == "country_filter":
        answer_text = _build_country_text(parsed, result_df)
    elif parsed.intent == "price_filter":
        answer_text = _build_price_filter_text(parsed, result_df)
    elif parsed.intent == "rating_filter":
        answer_text = _build_rating_filter_text(parsed, result_df)
    elif parsed.intent == "color_filter":
        answer_text = _build_color_filter_text(parsed, result_df)
    elif parsed.intent == "recommendation_gift":
        answer_text = _build_gift_text(result_df)
    else:
        answer_text = _build_general_search_text(result_df)

    results = [_row_to_result(row, parsed.intent) for _, row in result_df.iterrows()]
    return _response(
        question=question,
        parsed=parsed,
        answer_text=answer_text,
        results=results,
        loaded_from=loaded_from,
    )


def _apply_filters(df: pd.DataFrame, parsed: ParsedQuery) -> pd.DataFrame:
    filtered = df.copy()

    if parsed.price_max is not None:
        filtered = filtered[filtered["price"].notna() & (filtered["price"] <= parsed.price_max)]
    if parsed.price_min is not None:
        filtered = filtered[filtered["price"].notna() & (filtered["price"] >= parsed.price_min)]
    if parsed.min_rating is not None:
        filtered = filtered[filtered["rating"].notna() & (filtered["rating"] >= parsed.min_rating)]
    if parsed.country:
        normalized = _normalize_cached(parsed.country)
        filtered = filtered[filtered["country_normalized"] == normalized]
    if parsed.intent == "region_filter" and (parsed.region or parsed.appellation):
        location_masks = []
        if parsed.region:
            location_masks.append(filtered["region_normalized"] == _normalize_cached(parsed.region))
        if parsed.appellation:
            location_masks.append(filtered["appellation_normalized"] == _normalize_cached(parsed.appellation))
        if location_masks:
            combined_mask = location_masks[0]
            for mask in location_masks[1:]:
                combined_mask = combined_mask | mask
            filtered = filtered[combined_mask]
    else:
        if parsed.region:
            normalized = _normalize_cached(parsed.region)
            filtered = filtered[filtered["region_normalized"] == normalized]
        if parsed.appellation:
            normalized = _normalize_cached(parsed.appellation)
            filtered = filtered[filtered["appellation_normalized"] == normalized]
    if parsed.varietal:
        normalized = _normalize_cached(parsed.varietal)
        filtered = filtered[filtered["varietal_normalized"] == normalized]
    if parsed.color:
        normalized = _normalize_cached(parsed.color)
        filtered = filtered[filtered["color_normalized"] == normalized]

    if parsed.intent == "general_search":
        tokens = parsed.extracted_keywords or [token for token in parsed.normalized_question.split() if len(token) > 2]
        if tokens:
            filtered = filtered[filtered["search_blob"].map(lambda value: all(token in value for token in tokens))]

    return filtered


def _normalize_cached(value: str) -> str:
    from app.utils.text_utils import normalize_text

    return normalize_text(value)


def _build_most_expensive_text(df: pd.DataFrame) -> str:
    top = df.iloc[0]
    return (
        f"The most expensive bottle in the dataset is {top['name']} "
        f"from {top['region'] or top['country']} at ${top['price']:.2f}."
    )


def _build_best_under_price_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    if df.empty:
        return "I could not find any wines under that price in the dataset."
    return (
        f"Here are the top-rated wines in the dataset under ${parsed.price_max:.0f}, "
        "ranked by the average available critic score."
    )


def _build_region_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    location = parsed.region or parsed.appellation or "that region"
    qualifiers = _build_qualifier_text(parsed, exclude={location.lower()})
    return f"Here are the strongest matches I found in the dataset for {location}{qualifiers}, ranked by rating and then price."


def _build_country_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    qualifiers = _build_qualifier_text(parsed, exclude={parsed.country.lower() if parsed.country else ""})
    return f"Here are wines from {parsed.country}{qualifiers} in the dataset, ranked by average critic rating."


def _build_price_filter_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    if parsed.price_min is not None and parsed.price_max is not None:
        return f"Here are wines in the dataset priced between ${parsed.price_min:.0f} and ${parsed.price_max:.0f}."
    if parsed.price_max is not None:
        return f"Here are wines in the dataset priced under ${parsed.price_max:.0f}."
    return f"Here are wines in the dataset priced above ${parsed.price_min:.0f}."


def _build_rating_filter_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    if parsed.min_rating is not None:
        return f"Here are wines with an average critic rating of at least {parsed.min_rating:.0f}."
    return "Here are the best-rated wines in the dataset."


def _build_gift_text(df: pd.DataFrame) -> str:
    return (
        "These bottles are a grounded housewarming-style recommendation based on the dataset only: "
        "I prioritized wines with strong critic ratings and gift-friendly price points. "
        "The dataset does not explicitly label wines as gifts."
    )


def _build_general_search_text(df: pd.DataFrame) -> str:
    return "Here are the closest matches I found in the dataset."


def _build_color_filter_text(parsed: ParsedQuery, df: pd.DataFrame) -> str:
    descriptor = parsed.color or parsed.varietal or "those wines"
    qualifiers = _build_qualifier_text(parsed, exclude={descriptor.lower()})
    return f"Here are the strongest matches I found in the dataset for {descriptor}{qualifiers}, ranked by rating and then price."


def _build_qualifier_text(parsed: ParsedQuery, exclude: set[str] | None = None) -> str:
    exclude = exclude or set()
    parts: list[str] = []

    if parsed.country and parsed.country.lower() not in exclude:
        parts.append(f"from {parsed.country}")
    if parsed.region and parsed.region.lower() not in exclude:
        parts.append(f"from {parsed.region}")
    if parsed.appellation and parsed.appellation.lower() not in exclude:
        parts.append(f"in {parsed.appellation}")
    if parsed.color and parsed.color.lower() not in exclude:
        parts.append(f"that are {parsed.color}")
    if parsed.varietal and parsed.varietal.lower() not in exclude:
        parts.append(f"made from {parsed.varietal}")
    if parsed.price_max is not None:
        parts.append(f"under ${parsed.price_max:.0f}")
    if parsed.price_min is not None:
        parts.append(f"above ${parsed.price_min:.0f}")

    if not parts:
        return ""

    return " " + " ".join(parts)


def _row_to_result(row: pd.Series, intent: str) -> WineResult:
    match_reason = None
    if intent == "recommendation_gift":
        match_reason = "Selected using a transparent gift heuristic: strong rating plus gift-friendly price."
    elif intent in {"best_rated_under_price", "rating_filter"}:
        match_reason = "Ranked by average critic rating derived from professional_ratings."
    elif intent == "most_expensive":
        match_reason = "Ranked by retail price."

    return WineResult(
        id=int(row["id"]) if pd.notna(row["id"]) else None,
        name=row["name"],
        producer=row["producer"] or None,
        country=row["country"] or None,
        region=row["region"] or None,
        appellation=row["appellation"] or None,
        varietal=row["varietal"] or None,
        color=row["color"] or None,
        vintage=row["vintage"] or None,
        price=float(row["price"]) if pd.notna(row["price"]) else None,
        rating=float(row["rating"]) if pd.notna(row["rating"]) else None,
        rating_count=int(row["rating_count"]) if pd.notna(row["rating_count"]) else None,
        abv=float(row["abv"]) if pd.notna(row["abv"]) else None,
        volume_ml=float(row["volume_ml"]) if pd.notna(row["volume_ml"]) else None,
        reference_url=row["reference_url"] or None,
        image_url=row["image_url"] or None,
        summary_note=row["summary_note"] or None,
        match_reason=match_reason,
    )


def _response(
    *,
    question: str,
    parsed: ParsedQuery,
    answer_text: str,
    results: list[WineResult],
    loaded_from: str,
    clarification_needed: bool = False,
    unsupported: bool = False,
    reason: str | None = None,
) -> AskResponse:
    return AskResponse(
        question=question,
        intent=parsed.intent,
        answer_text=answer_text,
        results=results,
        meta=ResponseMeta(
            grounded=True,
            clarification_needed=clarification_needed,
            unsupported=unsupported,
            reason=reason,
            result_count=len(results),
            loaded_from=loaded_from,
        ),
    )


def _suggest_for_ambiguous_query(df: pd.DataFrame, parsed: ParsedQuery) -> list[WineResult]:
    tokens = [token for token in parsed.extracted_keywords if len(token) > 2]
    if not tokens:
        return []

    suggested = df[df["search_blob"].map(lambda value: any(token in value for token in tokens))]
    if suggested.empty:
        return []

    suggested = suggested.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(3)
    return [_row_to_result(row, "general_search") for _, row in suggested.iterrows()]
