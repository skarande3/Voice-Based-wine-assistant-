from __future__ import annotations

import json
import logging

from app.config import settings
from app.models import Catalog, ParsedQuery
from app.services.query_parser import parse_question
from app.utils.match_utils import exact_or_partial_match, fuzzy_match

logger = logging.getLogger(__name__)


class OpenAIQueryParser:
    def __init__(self) -> None:
        self._client = None
        self._catalog = Catalog()
        if settings.openai_enabled:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception as exc:  # pragma: no cover - import/runtime env failure path
                logger.warning("OpenAI SDK is unavailable: %s", exc)
                self._client = None

    def parse(self, question: str, catalog: Catalog) -> ParsedQuery:
        rule_result = parse_question(question, catalog)
        if not settings.openai_enabled or self._client is None:
            return rule_result

        if self._should_keep_rule_result(rule_result):
            return rule_result

        llm_result = self._parse_with_openai(question, catalog)
        if llm_result is None:
            return rule_result

        return self._merge(rule_result, llm_result)

    def _should_keep_rule_result(self, parsed: ParsedQuery) -> bool:
        if parsed.intent in {"best_rated_under_price", "region_filter", "country_filter", "most_expensive", "price_filter", "rating_filter"}:
            return True
        if parsed.intent == "color_filter":
            return True
        return False

    def _parse_with_openai(self, question: str, catalog: Catalog) -> dict | None:
        prompt = self._build_prompt(question, catalog)
        schema = {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "intent": {
                    "type": "string",
                    "enum": [
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
                    ],
                },
                "price_max": {"type": ["number", "null"]},
                "price_min": {"type": ["number", "null"]},
                "min_rating": {"type": ["number", "null"]},
                "region": {"type": ["string", "null"]},
                "country": {"type": ["string", "null"]},
                "appellation": {"type": ["string", "null"]},
                "varietal": {"type": ["string", "null"]},
                "color": {"type": ["string", "null"]},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "needs_clarification": {"type": "boolean"},
                "clarification_message": {"type": ["string", "null"]},
                "unsupported_reason": {"type": ["string", "null"]},
                "recommendation_context": {"type": ["string", "null"]},
                "confidence": {"type": "number"},
            },
            "required": [
                "intent",
                "price_max",
                "price_min",
                "min_rating",
                "region",
                "country",
                "appellation",
                "varietal",
                "color",
                "keywords",
                "needs_clarification",
                "clarification_message",
                "unsupported_reason",
                "recommendation_context",
                "confidence",
            ],
        }

        try:
            response = self._client.responses.create(
                model=settings.openai_model,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "wine_query_parse",
                        "strict": True,
                        "schema": schema,
                    }
                },
            )
            return json.loads(response.output_text)
        except Exception as exc:  # pragma: no cover - network/external failure path
            logger.warning("OpenAI parse fallback failed: %s", exc)
            return None

    def _build_prompt(self, question: str, catalog: Catalog) -> list[dict]:
        return [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "You are a query parser for a wine dataset application. "
                            "Your job is to convert a vague user question into structured search fields. "
                            "Do not answer the question. "
                            "Be conservative. If the user asks for something unsupported by the dataset, mark it unsupported. "
                            "If the request is too vague, mark it ambiguous and ask one short clarification question. "
                            "Only use these intents: best_rated_under_price, region_filter, country_filter, most_expensive, "
                            "price_filter, rating_filter, recommendation_gift, color_filter, general_search, unsupported, ambiguous."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            f"Question: {question}\n\n"
                            f"Supported countries: {', '.join(catalog.countries[:25])}\n"
                            f"Supported regions: {', '.join(catalog.regions[:40])}\n"
                            f"Supported appellations sample: {', '.join(catalog.appellations[:40])}\n"
                            f"Supported varietals: {', '.join(catalog.varietals[:30])}\n"
                            f"Supported colors: {', '.join(catalog.colors)}\n\n"
                            "Extract likely keywords and constraints. "
                            "For recommendation_gift, infer only from budget/rating/style-like hints and note low confidence if vague."
                        ),
                    }
                ],
            },
        ]

    def _merge(self, rule_result: ParsedQuery, llm_result: dict) -> ParsedQuery:
        merged = ParsedQuery(
            raw_question=rule_result.raw_question,
            normalized_question=rule_result.normalized_question,
            intent=llm_result.get("intent", rule_result.intent),
            price_max=llm_result.get("price_max"),
            price_min=llm_result.get("price_min"),
            min_rating=llm_result.get("min_rating"),
            region=self._resolve_catalog_value(llm_result.get("region"), "regions"),
            country=self._resolve_catalog_value(llm_result.get("country"), "countries"),
            appellation=self._resolve_catalog_value(llm_result.get("appellation"), "appellations"),
            varietal=self._resolve_catalog_value(llm_result.get("varietal"), "varietals"),
            color=self._resolve_catalog_value(llm_result.get("color"), "colors"),
            needs_clarification=bool(llm_result.get("needs_clarification", False)),
            clarification_message=llm_result.get("clarification_message"),
            unsupported_reason=llm_result.get("unsupported_reason"),
            recommendation_context=llm_result.get("recommendation_context"),
            extracted_keywords=[str(item).strip() for item in llm_result.get("keywords", []) if str(item).strip()],
            parse_source="openai",
            confidence=float(llm_result.get("confidence", 0.6)),
        )

        if not merged.intent:
            return rule_result

        if merged.intent in {"ambiguous", "unsupported"}:
            return merged

        if rule_result.intent not in {"ambiguous", "unsupported", "general_search"} and rule_result.confidence >= merged.confidence:
            return rule_result

        if merged.intent == "general_search" and not merged.extracted_keywords:
            merged.extracted_keywords = rule_result.extracted_keywords

        return merged

    def _resolve_catalog_value(self, candidate: str | None, field_name: str) -> str | None:
        if not candidate:
            return None
        catalog_values = getattr(self._catalog, field_name)
        direct = exact_or_partial_match(candidate, catalog_values)
        if direct:
            return direct
        return fuzzy_match(candidate, catalog_values, settings.fuzzy_match_threshold)


openai_query_parser = OpenAIQueryParser()


def parse_question_hybrid(question: str, catalog: Catalog) -> ParsedQuery:
    openai_query_parser._catalog = catalog
    return openai_query_parser.parse(question, catalog)
