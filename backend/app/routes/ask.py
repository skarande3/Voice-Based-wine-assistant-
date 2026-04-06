from fastapi import APIRouter, HTTPException

from app.schemas import AskRequest, AskResponse, RefreshResponse
from app.services.answer_engine import answer_question
from app.services.dataset_loader import dataset_store
from app.services.openai_query_parser import parse_question_hybrid

router = APIRouter(tags=["ask"])


@router.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest) -> AskResponse:
    if not dataset_store.is_loaded():
        try:
            dataset_store.load()
        except Exception as exc:  # pragma: no cover - defensive API guard.
            raise HTTPException(status_code=503, detail=f"Dataset is not available: {exc}") from exc

    df = dataset_store.dataframe()
    metadata = dataset_store.metadata()
    parsed = parse_question_hybrid(payload.question, dataset_store.catalog())
    response = answer_question(
        payload.question,
        parsed,
        df,
        loaded_from=str(metadata["loaded_from"]),
    )
    response.meta.source_row_count = int(metadata["row_count"])
    return response


@router.post("/refresh-data", response_model=RefreshResponse)
def refresh_data() -> RefreshResponse:
    snapshot = dataset_store.load()
    return RefreshResponse(
        success=True,
        row_count=snapshot.row_count,
        loaded_from=snapshot.loaded_from,
        loaded_at=snapshot.loaded_at,
    )
