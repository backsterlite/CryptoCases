from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List, Dict, Any
from pydantic import Field
import os

if "/app" in str(Path.cwd()):
    BASE_DIR = Path(__file__).resolve().parents[3]
else:
    BASE_DIR = Path(__file__).resolve().parents[4]

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db_name: str = "cryptocases"
    bot_token: str = ""
    jwt_secret: str = "supersecret"
    debug: bool = False
    COINGECKO_API: str = ""
    COINGECKO_BASE_URL: str = ""
    coin_registry_path: Path = BASE_DIR / "data" / "coin_registry.json"
    network_registry_path: Path = BASE_DIR / "data" / "network_registry.json"
    project_root_path: Path = BASE_DIR
    BASE_TOKENS: List[str] = ["TETHER", "USD-COIN"]
    local_odds_dir: Path = BASE_DIR / "data" / "odds"
    
    #REDIS
    REDIS_URL: str = Field(
        ...,
        description="URL for Redis (refresh tokens storage)"
    )
    REDIS_PASS: str = Field(
        default="",
        description="Password for Redis"
    )
    
     # HD wallet XPUB-ключі для кожної монети+мережі
    XPUB_USDT_ERC20: str = Field(..., description="XPUB для USDT ERC20")
    XPUB_USDT_TRC20: str = Field(..., description="XPUB для USDT TRC20")
    XPUB_USDC_ERC20: str = Field(..., description="XPUB для USDC ERC20")
    XPUB_TON_TONCENTER: str = Field(..., description="XPUB для TON")
    
    HD_XPRV: str = ""

    # BIP32-шаблон шляху для похідних адрес (останній сегмент — index)
    HD_DERIVATION_PATH_TEMPLATE: str = Field(
        "m/44'/{coin_index}'/0'/0/{index}", 
        description="BIP32 шлях: заміняються {coin_index} та {index}"
    )

    # Solana settings
    SOLANA_MAINNET_RPC_URL: str = ""
    SOLANA_TESTNET_RPC_URL: str = ""
    SOLANA_DEVNET_RPC_URL: str = ""
    SOLANA_NETWORK: str = "devnet" 
    SOLANA_SECRET_KEY:str=""

    # EVM Settings
    ETH_RPC_URL:        str = os.getenv("ETH_RPC_URL", "https://mainnet.infura.io/v3/your-project-id")
    ETH_CHAIN_ID:       int = int(os.getenv("ETH_CHAIN_ID", "1"))
    ETH_GAS_LIMIT:      int = int(os.getenv("ETH_GAS_LIMIT", "21000"))
    ETH_GAS_PRICE_GWEI: int = int(os.getenv("ETH_GAS_PRICE_GWEI", "50"))
    EVM_PRIVATE_KEY:str = ""

    TRON_PRIVATE_KEY:str= ""
    # ERC20 ABI
    ERC20_ABI : List[Dict[str, Any]] = [
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

    # Celery settings
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="URL для Celery broker (Redis)"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="URL для Celery result backend (Redis)"
    )

    model_config = SettingsConfigDict(
        env_file=Path(BASE_DIR, ".env"),
        env_prefix="BACKEND_",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=True,
        extra="ignore"
    )
    

settings = Settings()
