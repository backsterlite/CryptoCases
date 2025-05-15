from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

if "/app" in str(Path.cwd()):
    BASE_DIR = Path(__file__).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[4]
class TestSettings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "test_cryptocases"
    dev_bot_token: str

    model_config = SettingsConfigDict(
        env_file=Path(BASE_DIR,".env.test"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
    )
    

settings = TestSettings()