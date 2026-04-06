from fastapi import APIRouter

from app.schemas import HealthResponse
from app.services.dataset_loader import dataset_store

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    metadata = dataset_store.metadata()
    return HealthResponse(
        status="ok" if dataset_store.is_loaded() else "degraded",
        dataset_loaded=dataset_store.is_loaded(),
        row_count=int(metadata["row_count"]),
        loaded_from=str(metadata["loaded_from"] or ""),
        loaded_at=str(metadata["loaded_at"] or ""),
    )
