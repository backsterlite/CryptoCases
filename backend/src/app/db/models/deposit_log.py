from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Literal

from beanie import Document, Indexed
from pymongo import ASCENDING, IndexModel
from pydantic import Field



class DepositLog(Document):
    external_wallet_id: str = Field(..., description="Reference to ExternalWallet")
    tx_hash: str = Field(..., description="Transaction identifier on-chain")
    coin: str = Field(..., description="Asset symbol")
    amount: Decimal = Field(..., description="Amount deposited")
    from_address: Optional[str] = Field(None, description="Sender address")
    block_number: Optional[int] = Field(None, description="Block number of transaction inclusion")
    timestamp: Optional[datetime] = Field(None, description="On-chain timestamp of block")
    confirmations: int = Field(default=0, description="Number of confirmations seen")
    status: Literal['pending_onchain', 'pending_internal', 'confirmed', 'failed'] = Field(
        default='pending_onchain', description="Current status of deposit flow"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "deposit_logs"
        indexes = [
            
            IndexModel(
                [("tx_hash", ASCENDING)],
                unique=True
            )
        ]