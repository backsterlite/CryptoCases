from beanie import Document
from pydantic import Field
from datetime import datetime, timezone
from typing import Literal

class WithdrawalLog(Document):
    user_id: str
    token: str
    network: str
    amount: str  # stored as stringified Decimal
    address: str
    tx_hash: str
    status: Literal["pending", "success", "failed", "rejected"] = "success"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "withdrawal_logs"