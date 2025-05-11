from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db_name: str = "cryptocases"
    bot_token: str = "your_telegram_token"
    jwt_secret: str = "supersecret"
    debug: bool = False
    COINGECKO_API: str
    coin_registry_path: Path = BASE_DIR / "data" / "coin_registry.json"

    model_config = SettingsConfigDict(
        env_file="/app/.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
    )


settings = Settings()
