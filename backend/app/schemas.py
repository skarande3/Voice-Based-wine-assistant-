from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question about the wine dataset")


class WineResult(BaseModel):
    id: int | None = None
    name: str
    producer: str | None = None
    country: str | None = None
    region: str | None = None
    appellation: str | None = None
    varietal: str | None = None
    color: str | None = None
    vintage: str | None = None
    price: float | None = None
    rating: float | None = None
    rating_count: int | None = None
    abv: float | None = None
    volume_ml: float | None = None
    reference_url: str | None = None
    image_url: str | None = None
    summary_note: str | None = None
    match_reason: str | None = None


class ResponseMeta(BaseModel):
    grounded: bool = True
    clarification_needed: bool = False
    unsupported: bool = False
    reason: str | None = None
    result_count: int = 0
    source_row_count: int | None = None
    loaded_from: str | None = None


class AskResponse(BaseModel):
    success: bool = True
    question: str
    intent: str
    answer_text: str
    results: list[WineResult]
    meta: ResponseMeta


class HealthResponse(BaseModel):
    status: str
    dataset_loaded: bool
    row_count: int
    loaded_from: str | None = None
    loaded_at: str | None = None


class RefreshResponse(BaseModel):
    success: bool
    row_count: int
    loaded_from: str
    loaded_at: str


class WinesResponse(BaseModel):
    success: bool = True
    total: int
    results: list[WineResult]
