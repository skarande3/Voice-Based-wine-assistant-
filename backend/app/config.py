from dataclasses import dataclass, field
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass
class Settings:
    app_name: str = "Onki Voice Wine Explorer API"
    app_version: str = "0.1.0"
    csv_export_url: str = (
        "https://docs.google.com/spreadsheets/d/1Bkv3Jb_8YuLUG2rWUhJhQBdaGjQCMFfwF9oJ5jrYDSA/export?format=csv"
    )
    local_dataset_path: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[2] / "Copy of Assignment wine dataset.xlsx"
    )
    request_timeout_seconds: float = 20.0
    default_result_limit: int = 5
    max_result_limit: int = 25
    fuzzy_match_threshold: int = 92
    openai_model: str = "gpt-4.1-mini"
    openai_enabled: bool = False
    openai_api_key: str | None = None
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    @classmethod
    def from_env(cls) -> "Settings":
        base = cls()

        dataset_override = os.getenv("ONKI_LOCAL_DATASET_PATH")
        if dataset_override:
            base.local_dataset_path = Path(dataset_override).expanduser().resolve()

        csv_override = os.getenv("ONKI_CSV_EXPORT_URL")
        if csv_override:
            base.csv_export_url = csv_override

        model_override = os.getenv("ONKI_OPENAI_MODEL")
        if model_override:
            base.openai_model = model_override

        cors_override = os.getenv("ONKI_CORS_ORIGINS")
        if cors_override:
            base.cors_origins = [origin.strip() for origin in cors_override.split(",") if origin.strip()]

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_real_key_here":
            base.openai_api_key = api_key
            base.openai_enabled = True

        return base


settings = Settings.from_env()
