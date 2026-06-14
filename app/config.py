from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/glasses_bot"
    log_level: str = "INFO"
    source_products_csv: Path = Path(r"C:\Users\enter\Downloads\best_sellers_amazon_2024_sunglasses.csv")
    normalized_products_csv: Path = Path("app/datasets/products.csv")
    synthetic_products_csv: Path = Path("app/datasets/synthetic_products.csv")
    intents_csv: Path = Path("app/datasets/intents.csv")
    ner_dataset_json: Path = Path("app/datasets/ner_dataset.json")
    dialogues_txt: Path = Path("app/datasets/dialogues.txt")
    vosk_model_path: Path = Path("models/vosk-model-small-ru-0.22")
    piper_model_path: Path | None = Path("models/piper/ru_RU-dmitri-medium.onnx")
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    llm_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
