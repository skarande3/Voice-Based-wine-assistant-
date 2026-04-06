from __future__ import annotations

import re

from app.config import settings
from app.models import Catalog, ParsedQuery
from app.utils.match_utils import exact_or_partial_match, fuzzy_match
from app.utils.text_utils import normalize_text

TOP_RATED_PHRASES = ("best", "best-rated", "highest rated", "highest-rated", "top rated", "top")
GIFT_PHRASES = ("gift", "present", "housewarming", "host", "hosting")
PAIRING_PHRASES = ("pair", "pairing", "with sushi", "with seafood", "with steak", "with pasta")
VAGUE_RECOMMENDATION_PHRASES = ("recommend", "good", "nice", "something", "maybe", "suggest", "help me choose")
ENTITY_ALIASES = {
    "burgundy": ("bourgogne", "burgundy"),
    "napa": ("napa valley", "napa"),
    "sparkling": ("sparkling", "champagne", "prosecco"),
    "bubbly": ("sparkling", "champagne", "prosecco"),
    "french": ("france",),
    "italian": ("italy",),
    "californian": ("california",),
}


def parse_question(question: str, catalog: Catalog) -> ParsedQuery:
    normalized_question = normalize_text(question)
    parsed = ParsedQuery(
        raw_question=question.strip(),
        normalized_question=normalized_question,
        intent="general_search",
    )

    if not parsed.raw_question:
        parsed.intent = "ambiguous"
        parsed.needs_clarification = True
        parsed.clarification_message = (
            "I can help with price, rating, region, country, and gift-style questions. "
            "Try asking something like 'best-rated wines under $50'."
        )
        return parsed

    if any(phrase in normalized_question for phrase in PAIRING_PHRASES):
        parsed.intent = "unsupported"
        parsed.unsupported_reason = (
            "The dataset does not include food-pairing information, so I cannot answer that reliably."
        )
        return parsed

    parsed.price_max, parsed.price_min = _extract_price_bounds(normalized_question)
    parsed.min_rating = _extract_min_rating(normalized_question)
    parsed.country = _match_entity(normalized_question, catalog.countries)
    parsed.region = _match_entity(normalized_question, catalog.regions)
    parsed.appellation = _match_entity(normalized_question, catalog.appellations)
    parsed.varietal = _match_entity(normalized_question, catalog.varietals, use_fuzzy=False)
    parsed.color = _match_entity(normalized_question, catalog.colors, use_fuzzy=False)

    if parsed.varietal and normalize_text(parsed.varietal) not in normalized_question:
        parsed.varietal = None
    if parsed.color and normalize_text(parsed.color) not in normalized_question:
        parsed.color = None

    if any(phrase in normalized_question for phrase in ("most expensive", "highest price", "priciest")):
        parsed.intent = "most_expensive"
        parsed.sort_by = "price"
        parsed.sort_order = "desc"
        return parsed

    if any(phrase in normalized_question for phrase in GIFT_PHRASES):
        parsed.intent = "recommendation_gift"
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        parsed.recommendation_context = "gift"
        return parsed

    if any(phrase in normalized_question for phrase in TOP_RATED_PHRASES):
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        if parsed.price_max is not None:
            parsed.intent = "best_rated_under_price"
        else:
            parsed.intent = "rating_filter"
        return parsed

    if parsed.region or parsed.appellation:
        parsed.intent = "region_filter"
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        return parsed

    if parsed.country:
        parsed.intent = "country_filter"
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        return parsed

    if parsed.color or parsed.varietal:
        parsed.intent = "color_filter" if parsed.color else "general_search"
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        return parsed

    if parsed.price_min is not None or parsed.price_max is not None:
        parsed.intent = "price_filter"
        parsed.sort_by = "price"
        parsed.sort_order = "asc"
        return parsed

    if parsed.min_rating is not None:
        parsed.intent = "rating_filter"
        parsed.sort_by = "rating"
        parsed.sort_order = "desc"
        return parsed

    if any(word in normalized_question for word in ("recommend", "good", "nice")):
        parsed.intent = "ambiguous"
        parsed.needs_clarification = True
        parsed.extracted_keywords = _extract_keywords(normalized_question)
        parsed.clarification_message = _build_clarification_message(parsed)
        return parsed

    if any(word in normalized_question for word in ("show", "find", "have", "wines", "bottles")):
        parsed.intent = "general_search"
        parsed.extracted_keywords = _extract_keywords(normalized_question)
        parsed.confidence = 0.5
        return parsed

    if any(phrase in normalized_question for phrase in VAGUE_RECOMMENDATION_PHRASES):
        parsed.intent = "ambiguous"
        parsed.needs_clarification = True
        parsed.extracted_keywords = _extract_keywords(normalized_question)
        parsed.clarification_message = _build_clarification_message(parsed)
        parsed.confidence = 0.35
        return parsed

    parsed.intent = "ambiguous"
    parsed.needs_clarification = True
    parsed.extracted_keywords = _extract_keywords(normalized_question)
    parsed.clarification_message = (
        "I can help with wines by price, rating, region, country, color, varietal, or gift-style suggestions. "
        "Tell me one of those constraints and I can narrow it down."
    )
    parsed.confidence = 0.3
    return parsed


def _extract_price_bounds(question: str) -> tuple[float | None, float | None]:
    price_max = None
    price_min = None

    under_match = re.search(r"(under|below|less than|cheaper than)\s+\$?(\d+)", question)
    if under_match:
        price_max = float(under_match.group(2))

    over_match = re.search(r"(over|above|more than)\s+\$?(\d+)", question)
    if over_match:
        price_min = float(over_match.group(2))

    between_match = re.search(r"between\s+\$?(\d+)\s+(and|to)\s+\$?(\d+)", question)
    if between_match:
        first = float(between_match.group(1))
        second = float(between_match.group(3))
        price_min = min(first, second)
        price_max = max(first, second)

    return price_max, price_min


def _extract_min_rating(question: str) -> float | None:
    match = re.search(r"(rated|rating|score)\s+(above|over|at least|>=)\s+(\d+)", question)
    if match:
        return float(match.group(3))

    shorthand_match = re.search(r"(\d{2})\+?\s*points", question)
    if shorthand_match:
        return float(shorthand_match.group(1))

    return None


def _match_entity(question: str, choices: list[str], *, use_fuzzy: bool = True) -> str | None:
    alias_match = _match_alias(question, choices)
    if alias_match:
        return alias_match

    direct = exact_or_partial_match(question, choices)
    if direct:
        return direct
    if use_fuzzy:
        return fuzzy_match(question, choices, settings.fuzzy_match_threshold)
    return None


def _match_alias(question: str, choices: list[str]) -> str | None:
    for alias, targets in ENTITY_ALIASES.items():
        if alias not in question:
            continue
        for choice in choices:
            normalized_choice = normalize_text(choice)
            if any(target in normalized_choice for target in targets):
                return choice
    return None


def _extract_keywords(question: str) -> list[str]:
    stopwords = {
        "what", "which", "that", "this", "with", "from", "have", "would", "make", "good",
        "nice", "some", "something", "maybe", "show", "find", "wine", "wines", "bottles",
        "recommend", "suggest", "help", "choose", "please", "about",
    }
    return [token for token in question.replace("?", "").split() if len(token) > 2 and token not in stopwords]


def _build_clarification_message(parsed: ParsedQuery) -> str:
    hints = []
    if parsed.country or parsed.region or parsed.appellation:
        hints.append("region")
    if parsed.color or parsed.varietal:
        hints.append("style")
    if parsed.price_max or parsed.price_min:
        hints.append("budget")

    if hints:
        return (
            "I found part of your request, but I need one more detail to narrow it down. "
            "You can add a budget, region, color, varietal, or occasion."
        )

    return (
        "I can suggest wines, but I need a bit more detail. "
        "Try adding a budget, region, color, varietal, or occasion."
    )
