from dataclasses import dataclass, field
from typing import Literal


IntentName = Literal[
    "best_rated_under_price",
    "region_filter",
    "country_filter",
    "most_expensive",
    "price_filter",
    "rating_filter",
    "recommendation_gift",
    "color_filter",
    "general_search",
    "unsupported",
    "ambiguous",
]


@dataclass
class Catalog:
    countries: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    appellations: list[str] = field(default_factory=list)
    varietals: list[str] = field(default_factory=list)
    colors: list[str] = field(default_factory=list)


@dataclass
class ParsedQuery:
    raw_question: str
    intent: IntentName
    normalized_question: str
    price_max: float | None = None
    price_min: float | None = None
    min_rating: float | None = None
    region: str | None = None
    country: str | None = None
    appellation: str | None = None
    varietal: str | None = None
    color: str | None = None
    sort_by: str | None = None
    sort_order: Literal["asc", "desc"] | None = None
    needs_clarification: bool = False
    unsupported_reason: str | None = None
    clarification_message: str | None = None
    recommendation_context: str | None = None
    extracted_keywords: list[str] = field(default_factory=list)
    parse_source: Literal["rules", "openai"] = "rules"
    confidence: float = 1.0


@dataclass
class DataSnapshot:
    dataframe_columns: list[str]
    row_count: int
    loaded_from: str
    loaded_at: str
