from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import Field

if "/app" in str(Path.cwd()):
    BASE_DIR = Path(__file__).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[4]
class TestSettings(BaseSettings):
    test_mongo_url: str = "mongodb://mongo:27017/?replicaSet=rs0"
    test_mongo_db_name: str = "test_cryptocases"
    dev_bot_token: str = Field(default="", description="Bot token for dev")

    model_config = SettingsConfigDict(
        env_file=Path(BASE_DIR, ".env.test"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
    )
    

settings = TestSettings()