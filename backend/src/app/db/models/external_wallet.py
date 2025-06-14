from datetime import datetime, timezone
from typing import Literal, Optional

from beanie import Document, Indexed
from pymongo import IndexModel, ASCENDING
from pydantic import Field

class ExternalWallet(Document):
    user_id: int = Field(..., description="User identifier")
    coin: str = Field(..., description="Asset symbol, e.g., USDT, ETH")
    network: str = Field(..., description="Blockchain network, e.g., ethereum, tron")
    address: str = Field(..., description="On-chain public address")
    wallet_type: Literal["deposit", "withdrawal"] = Field(..., description="wallet type")
    derivation_index: Optional[int] = Field(None, description="HD derivation index used to generate this address")
    derivation_path: Optional[str] = Field(None, description="Full BIP32 derivation path")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "external_wallets"
        indexes = [
            IndexModel(
                [
                    ("user_id", ASCENDING),
                    ("coin", ASCENDING),
                    ("network", ASCENDING),
                    ("address", ASCENDING),
                ],
                name="unique_user_coin_network_address_index",
                unique=True
            )
        ]

