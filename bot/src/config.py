from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field



BASE_DIR = Path(__file__).resolve().parents[1]

print(f"BASE_DIR: {BASE_DIR}")


class Settings(BaseSettings):
    """
    Bot setup
    """
    # Telegram Bot Token
    BOT_TOKEN: str = Field(
        default="",
        description="Токен Telegram бота"
    )
    
    # WebApp URL
    WEBAPP_URL: str = Field(
        default="https://your-frontend-url.com",
        description="Frontend URL for WebApp"
    )
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding = "utf-8"
    )

# Create setup instance
settings = Settings() 