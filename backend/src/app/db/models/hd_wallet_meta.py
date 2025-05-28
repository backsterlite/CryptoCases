from beanie import Document, Indexed
from pydantic import Field
from typing import Optional
from pymongo import IndexModel, ASCENDING

class HDWalletMeta(Document):
    coin: str = Field(..., description="Asset , e.g., USDT, USDC, TON")
    network: str = Field(..., description="Network identifier, e.g., ERC20, TRC20, TON")
    xpub: str = Field(..., description="Master XPUB для цього coin+network")
    current_index: int = Field(0, description="Поточний index для деривації")

    class Settings:
        name = "hd_wallet_meta"
        indexes = [
            IndexModel(
                [("coin", ASCENDING), ("network", ASCENDING)],
                unique=True,
                name="unique_coin_network_index"
            )
        ]