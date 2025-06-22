from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pathlib import Path
from typing import List, Dict, Any


# Визначаємо корінь проекту
if "/app" in str(Path.cwd()):
    BASE_DIR = Path(__file__).resolve().parents[4]
else:
    BASE_DIR = Path(__file__).resolve().parents[4]

class Settings(BaseSettings):
    # MongoDB
    mongo_uri: str = Field(...)
    mongo_db_name: str = Field(...)

    # Telegram Bot та JWT
    bot_token: str = ""          # TELEGRAM BOT TOKEN (ENV: BACKEND_BOT_TOKEN)
    jwt_secret: str = Field(..., min_length=32)         # JWT SECRET (ENV: BACKEND_JWT_SECRET)
    
    @field_validator('jwt_secret')
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError('JWT secret must be at least 32 characters')
        return v

    # Debug / тестовий режим
    debug: bool = False
    
    
    COINGECKO_API: str = Field(...)
    COINGECKO_BASE_URL: str = Field(...)
    
    BASE_TOKENS: List[str] = ["tether", "usd-coin"]
    GLOBAL_USD_WALLET_ALIAS: List[str] = ["tether", "usdt", "usdc", "usd-coin"]
    ROLE_PRIORITIES: Dict[str,int] = {
        "user": 1,
        "worker": 2,
        "admin": 3
    }
    local_odds_dir: Path = BASE_DIR / "data" / "odds"
    
    # Шляхи до реєстрів
    coin_registry_path: Path = BASE_DIR / "data" / "coin_registry.json"
    network_registry_path: Path = BASE_DIR / "data" / "chain_registry.json"
    asset_registry_path: Path = BASE_DIR / "data" / "asset_registry.json"
    project_root_path: Path = BASE_DIR

    # Redis (refresh tokens, Celery)
    REDIS_URL: str = "redis://localhost:6379/1"
    REDIS_PASS: str = ""

    # HD-деривація: XPUB / SECRET KEY для кожної мережі
    TON_HD_XPUB: str = Field("", description="Master XPUB для HD-адрес у мережі TON")
    TRON_HD_XPUB: str = Field("", description="Master XPUB для HD-адрес у мережі TRON (TRC20)")
    POLYGON_HD_XPUB: str = Field("", description="Master XPUB для HD-адрес у мережі Polygon/Ethereum")
    SOLANA_HD_SECRET_KEY: str = Field("", description="Full Secret Key (Base58) для HD-адрес у мережі Solana")

    # Шаблони BIP32-дериваційних шляхів (останній сегмент — {index})
    HD_DERIVATION_PATH_TEMPLATE: str = Field(
        "m/44'/{coin_index}'/0'/0/{index}"
    )

    # TON Center API (якщо використовується для моніторингу TON)
    TONCENTER_API_KEY: str = Field("", description="API Key для toncenter (DEPLOY/моніторинг)")

    # (Опціонально) Custodial Keys (якщо використовуєте централізований гаманець)
    CUSTODIAL_TON_SECRET: str = Field("", description="Приватний ключ централізованого TON-гаманця (якщо є)")
    CUSTODIAL_TRON_PRIVATE_KEY: str = Field("", description="Приватний ключ централізованого TRON-гаманця")
    CUSTODIAL_POLYGON_PRIVATE_KEY: str = Field("", description="Приватний ключ централізованого Polygon (EVM) гаманця")
    CUSTODIAL_SOLANA_SECRET_KEY: str = Field("", description="Secret Key централізованого Solana-гаманця")

    # ABI для ERC20 (залишаємо для EVM-транзакцій)
    ERC20_ABI: List[Dict[str, Any]] = [
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]
    
    MNEMONIC: str = Field(..., description="secret mnemonic")

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=Path(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
        extra="ignore"
    )

@lru_cache
def get_settings():
    settings = Settings()
    return settings