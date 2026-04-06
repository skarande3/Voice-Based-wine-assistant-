from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas import WineResult, WinesResponse
from app.services.answer_engine import _row_to_result
from app.services.dataset_loader import dataset_store
from app.utils.text_utils import normalize_text

router = APIRouter(tags=["wines"])


@router.get("/wines", response_model=WinesResponse)
def list_wines(
    price_max: float | None = Query(default=None),
    price_min: float | None = Query(default=None),
    region: str | None = Query(default=None),
    country: str | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    limit: int = Query(default=settings.default_result_limit, ge=1, le=settings.max_result_limit),
) -> WinesResponse:
    if not dataset_store.is_loaded():
        try:
            dataset_store.load()
        except Exception as exc:  # pragma: no cover - defensive API guard.
            raise HTTPException(status_code=503, detail=f"Dataset is not available: {exc}") from exc

    df = dataset_store.dataframe()
    total_matches = len(df)

    if price_max is not None:
        df = df[df["price"].notna() & (df["price"] <= price_max)]
    if price_min is not None:
        df = df[df["price"].notna() & (df["price"] >= price_min)]
    if min_rating is not None:
        df = df[df["rating"].notna() & (df["rating"] >= min_rating)]
    if region:
        df = df[df["region_normalized"] == normalize_text(region)]
    if country:
        df = df[df["country_normalized"] == normalize_text(country)]

    total_matches = len(df)
    df = df.sort_values(by=["rating", "price"], ascending=[False, True], na_position="last").head(limit)
    results = [_row_to_result(row, "general_search") for _, row in df.iterrows()]
    return WinesResponse(total=total_matches, results=results)
