from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Literal

from beanie import Document
from pymongo import ASCENDING, DESCENDING, IndexModel
from pydantic import Field


class WithdrawalLog(Document):
    user_id: str = Field(..., description="User identifier")
    external_wallet_id: str = Field(..., description="Reference to ExternalWallet")
    network: str = Field(..., description="Asset network")
    to_address: str = Field(..., description="Destination on-chain address")
    amount_coin: Decimal = Field(..., description="Amount in coin units")
    amount_usdt: Decimal = Field(..., description="Equivalent in USDT for accounting")
    conversion_rate: Decimal = Field(..., description="Exchange rate used")
    fee_coin: Optional[Decimal] = Field(None, description="Fee in coin units")
    fee_usdt: Optional[Decimal] = Field(None, description="Fee in USDT equivalent")
    tx_hash: Optional[str] = Field(None, description="On-chain transaction hash")
    block_number: Optional[int] = Field(None, description="Block number of tx inclusion")
    confirmations: int = Field(default=0, description="Number of confirmations seen")
    status: Literal["pending", "pending_review", "approved", "broadcasted", "confirmed", "failed", "rejected"] = Field(
        default="pending", description="Current status of withdrawal flow"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "withdrawal_logs"
        indexes = [
            
            IndexModel(
                [("tx_hash",ASCENDING)],
                unique=True
            ),
            IndexModel(
                [("user_id", ASCENDING), ("created_at", DESCENDING)],
            )
        ]
