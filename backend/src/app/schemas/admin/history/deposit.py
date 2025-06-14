from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.history_status import StatusHistoryEntry 



class DepositHistoryEntry(BaseModel):
    """
    Повертається для адмінки: повний запис DepositLog з масивом status_history.
    """
    id: str                               # рядкове представлення ObjectId
    user_id: Optional[str]
    external_wallet_id: str
    tx_hash: str
    coin: str
    amount: Decimal
    from_address: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    confirmations: int
    status: str
    created_at: datetime
    updated_at: datetime

    # Масив усіх змін статусу (StatusHistoryEntry)
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60f7c2d5ab12cd3f5e678902",
                "user_id": "12345",
                "external_wallet_id": "wallet_abc",
                "tx_hash": "0xabc123...",
                "coin": "USDT",
                "amount": "100.50",
                "from_address": "0xsender...",
                "block_number": 12345678,
                "timestamp": "2025-06-02T11:05:00.000Z",
                "confirmations": 12,
                "status": "confirmed",
                "created_at": "2025-06-02T10:55:00.000Z",
                "updated_at": "2025-06-02T11:05:00.000Z",
                "status_history": [
                    {
                        "status": "pending_onchain",
                        "changed_at": "2025-06-02T10:55:00.000Z",
                        "actor_id": None,
                        "actor_role": None,
                        "reason": None,
                        "ip_address": None,
                        "user_agent": None,
                        "country": None
                    },
                    {
                        "status": "pending_internal",
                        "changed_at": "2025-06-02T10:58:00.000Z",
                        "actor_id": "system",
                        "actor_role": "worker",
                        "reason": "On-chain confirmed",
                        "ip_address": "203.0.113.42",
                        "user_agent": "nodejs/14.17.0",
                        "country": "UA"
                    },
                    {
                        "status": "confirmed",
                        "changed_at": "2025-06-02T11:05:00.000Z",
                        "actor_id": "admin_1",
                        "actor_role": "admin",
                        "reason": "Credit to internal balance",
                        "ip_address": "198.51.100.23",
                        "user_agent": "curl/7.78.0",
                        "country": "PL"
                    }
                ]
            }
        }
        
class DepositHistoryListResponse(BaseModel):
    deposits: List[DepositHistoryEntry]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "deposits": [
                    {
                        "id": "60f7c2d5ab12cd3f5e678902",
                        "user_id": "12345",
                        "external_wallet_id": "wallet_abc",
                        "tx_hash": "0xabc123...",
                        "coin": "USDT",
                        "amount": "100.50",
                        "from_address": "0xsender...",
                        "block_number": 12345678,
                        "timestamp": "2025-06-02T11:05:00.000Z",
                        "confirmations": 12,
                        "status": "confirmed",
                        "created_at": "2025-06-02T10:55:00.000Z",
                        "updated_at": "2025-06-02T11:05:00.000Z",
                        "status_history": [StatusHistoryEntry],
                    },
                ]
            }
        }
