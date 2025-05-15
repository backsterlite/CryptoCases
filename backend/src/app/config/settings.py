from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List
from dotenv import load_dotenv

if "/app" in str(Path.cwd()):
    BASE_DIR = Path(__file__).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[4]

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db_name: str = "cryptocases"
    bot_token: str = "your_telegram_token"
    jwt_secret: str = "supersecret"
    debug: bool = False
    COINGECKO_API: str
    COINGECKO_BASE_URL: str
    coin_registry_path: Path = BASE_DIR / "data" / "coin_registry.json"
    project_root_path: Path = BASE_DIR
    BASE_TOKENS: List[str] = ["TETHER", "USD-COIN"]
    local_odds_dir: Path = BASE_DIR / "data" / "odds"

    model_config = SettingsConfigDict(
        env_file=Path(BASE_DIR, ".env"),
        env_prefix="BACKEND_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
        extra="ignore"
    )
    

settings = Settings()
