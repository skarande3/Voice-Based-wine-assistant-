from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - used only when rapidfuzz is unavailable locally.
    fuzz = None

from app.utils.text_utils import normalize_text


def exact_or_partial_match(question: str, choices: list[str]) -> str | None:
    normalized_question = normalize_text(question)
    for choice in choices:
        normalized_choice = normalize_text(choice)
        if normalized_choice and (
            normalized_choice in normalized_question or normalized_question in normalized_choice
        ):
            return choice
    return None


def fuzzy_match(question: str, choices: list[str], threshold: int) -> str | None:
    normalized_question = normalize_text(question)
    best_choice: str | None = None
    best_score = threshold

    for choice in choices:
        normalized_choice = normalize_text(choice)
        if fuzz is not None:
            score = fuzz.partial_ratio(normalized_question, normalized_choice)
        else:
            score = int(SequenceMatcher(None, normalized_question, normalized_choice).ratio() * 100)
        if score >= best_score:
            best_choice = choice
            best_score = score

    return best_choice
