from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from app.models.history_status import StatusHistoryEntry



class WithdrawalHistoryEntry(BaseModel):
    """
    Повертається для адмінки: повний запис WithdrawalLog з масивом status_history.
    """
    id: str
    user_id: str
    external_wallet_id: str
    network: str
    to_address: str
    amount_coin: Decimal
    amount_usdt: Decimal
    conversion_rate: Decimal
    fee_coin: Optional[Decimal] = None
    fee_usdt: Optional[Decimal] = None
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
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
                "id": "60f7c2d5ab12cd3f5e678903",
                "user_id": "12345",
                "external_wallet_id": "wallet_xyz",
                "network": "tron",
                "to_address": "TXYZ...",
                "amount_coin": "50.0",
                "amount_usdt": "50.00",
                "conversion_rate": "1.00",
                "fee_coin": "0.1",
                "fee_usdt": "0.10",
                "tx_hash": "0xdef456...",
                "block_number": 12345679,
                "confirmations": 3,
                "status": "broadcasted",
                "created_at": "2025-06-02T15:30:00.000Z",
                "updated_at": "2025-06-02T15:40:00.000Z",
                "status_history": [
                    {
                        "status": "pending",
                        "changed_at": "2025-06-02T15:30:00.000Z",
                        "actor_id": None,
                        "actor_role": None,
                        "reason": None,
                        "ip_address": None,
                        "user_agent": None,
                        "country": None
                    },
                    {
                        "status": "approved",
                        "changed_at": "2025-06-02T15:32:00.000Z",
                        "actor_id": "admin_2",
                        "actor_role": "admin",
                        "reason": "KYC passed",
                        "ip_address": "198.51.100.24",
                        "user_agent": "PostmanRuntime/7.28.0",
                        "country": "PL"
                    },
                    {
                        "status": "broadcasted",
                        "changed_at": "2025-06-02T15:40:00.000Z",
                        "actor_id": "worker_3",
                        "actor_role": "worker",
                        "reason": "Broadcast to TRON network",
                        "ip_address": "203.0.113.43",
                        "user_agent": "curl/7.78.0",
                        "country": "UA"
                    }
                ]
            }
        }


class WithdrawalHistoryListResponse(BaseModel):
    withdrawals: List[WithdrawalHistoryEntry]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "withdrawals": [
                    {
                        "id": "60f7c2d5ab12cd3f5e678903",
                        "user_id": "12345",
                        "external_wallet_id": "wallet_xyz",
                        "network": "tron",
                        "to_address": "TXYZ...",
                        "amount_coin": "50.0",
                        "amount_usdt": "50.00",
                        "conversion_rate": "1.00",
                        "fee_coin": "0.1",
                        "fee_usdt": "0.10",
                        "tx_hash": "0xdef456...",
                        "block_number": 12345679,
                        "confirmations": 3,
                        "status": "broadcasted",
                        "created_at": "2025-06-02T15:30:00.000Z",
                        "updated_at": "2025-06-02T15:40:00.000Z",
                        "status_history": []
                    },
                    # інші записи...
                ]
            }
        }