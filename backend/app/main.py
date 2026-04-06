import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.ask import router as ask_router
from app.routes.health import router as health_router
from app.routes.wines import router as wines_router
from app.services.dataset_loader import dataset_store

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(wines_router)
app.include_router(ask_router)


@app.on_event("startup")
def startup_load_dataset() -> None:
    dataset_store.load()
