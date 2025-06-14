# src/app/schemas/history.py

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


# === 1. Схема історії спінів (для клієнта) ===
class SpinHistoryItem(BaseModel):
    id: str                   # рядкове представлення ObjectId
    case_id: str
    stake: Decimal
    payout: Decimal
    payout_usd: Optional[Decimal]
    prize_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60f7c2d5ab12cd3f5e678901",
                "case_id": "gold_case",
                "stake": "10.5",
                "payout": "25.0",
                "payout_usd": "25.00",
                "prize_id": "prize_123",
                "created_at": "2025-06-01T14:23:00.000Z"
            }
        }


class SpinHistoryResponse(BaseModel):
    spins: List[SpinHistoryItem]


# === 2. Схема історії депозитів ===
class DepositHistoryItem(BaseModel):
    id: str
    coin: str
    amount: Decimal
    status: str
    tx_hash: Optional[str]
    confirmations: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60f7c2d5ab12cd3f5e678902",
                "coin": "USDT",
                "amount": "100.5",
                "status": "confirmed",
                "tx_hash": "0xabc123...",
                "confirmations": 12,
                "created_at": "2025-06-02T11:05:00.000Z"
            }
        }


class DepositHistoryResponse(BaseModel):
    deposits: List[DepositHistoryItem]


# === 3. Схема історії виводів ===
class WithdrawalHistoryItem(BaseModel):
    id: str
    to_address: str
    amount_coin: Decimal
    fee_coin: Optional[Decimal]
    status: str
    tx_hash: Optional[str]
    confirmations: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60f7c2d5ab12cd3f5e678903",
                "to_address": "0xdef456...",
                "amount_coin": "50.0",
                "fee_coin": "0.1",
                "status": "broadcasted",
                "tx_hash": "0xdef456...",
                "confirmations": 3,
                "created_at": "2025-06-02T15:40:00.000Z"
            }
        }


class WithdrawalHistoryResponse(BaseModel):
    withdrawals: List[WithdrawalHistoryItem]
