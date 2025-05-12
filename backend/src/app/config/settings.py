import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db_name: str = "cryptocases"
    bot_token: str = "your_telegram_token"
    jwt_secret: str = "supersecret"
    debug: bool = False
    COINGECKO_API: str
    COINGECKO_BASE_URL: str
    coin_registry_path: Path = BASE_DIR / "data" / "coin_registry.json"
    BASE_TOKENS: List[str] 

    model_config = SettingsConfigDict(
        env_file="/app/.env",
        env_prefix="BACKEND_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
        extra="ignore"
    )
    
    @field_validator("BASE_TOKENS", mode="before")
    @classmethod
    def split_base_tokens(cls, v):
        if isinstance(v, str):
            # спробуємо JSON-парсинг, якщо не вийде — розіб’ємо по комам
            try:
                return json.loads(v)
            except Exception:
                return [item.strip() for item in v.split(",") if item.strip()]
        return v


settings = Settings()
