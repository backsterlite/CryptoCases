from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    mongo_url: str = "mongodb://localhost:27017"
    mongo_db_name: str = "test_cryptocases"
    dev_bot_token: str

    model_config = SettingsConfigDict(
        env_file="/app/.env.test",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
    )
    

settings = TestSettings()