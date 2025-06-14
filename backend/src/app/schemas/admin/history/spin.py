from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

class SpinLogEntry(BaseModel):
    id: str                     # рядкове представлення ObjectId
    user_id: int
    case_id: str
    server_seed_id: str
    server_seed_hash: str
    server_seed_seed: str
    client_seed: str
    nonce: int
    hmac_value: bytes
    raw_roll: Decimal
    table_id: str
    odds_version: str
    case_tier: str
    prize_id: Optional[str] = None
    stake: Decimal
    payout: Decimal
    payout_usd: Decimal
    pity_before: Decimal
    pity_after: Decimal
    rtp_session: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "60f7c2d5ab12cd3f5e678901",
                "user_id": 123,
                "case_id": "gold_case",
                "server_seed_id": "abcd1234",
                "server_seed_hash": "f5d8ee39efb...",
                "server_seed_seed": "5f4dcc3b5aa76...",
                "client_seed": "client123seed",
                "nonce": 42,
                "hmac_value": "bWVzc2FnZV9oY21hX3N0cmluZw==",  # Base64-рядок
                "raw_roll": "0.4532",
                "table_id": "table_1A",
                "odds_version": "v2",
                "case_tier": "premium",
                "prize_id": "prize_123",      # може бути None, якщо без призу
                "stake": "10.5",
                "payout": "25.0",
                "payout_usd": "25.00",
                "pity_before": "0.0500",
                "pity_after": "0.0600",
                "rtp_session": "0.9800",
                "created_at": "2025-06-01T14:23:00.000Z"
            }
        }


# Схема для відповіді зі списком SpinLog-ів
class SpinLogListResponse(BaseModel):
    spins: List[SpinLogEntry] = Field(default_factory=list)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "spins": [
                    {
                        "id": "60f7c2d5ab12cd3f5e678901",
                        "user_id": 123,
                        "case_id": "gold_case",
                        "server_seed_id": "abcd1234",
                        "server_seed_hash": "f5d8ee39efb...",
                        "server_seed_seed": "5f4dcc3b5aa76...",
                        "client_seed": "client123seed",
                        "nonce": 42,
                        "hmac_value": "bWVzc2FnZV9oY21hX3N0cmluZw==",
                        "raw_roll": "0.4532",
                        "table_id": "table_1A",
                        "odds_version": "v2",
                        "case_tier": "premium",
                        "prize_id": "prize_123",
                        "stake": "10.5",
                        "payout": "25.0",
                        "payout_usd": "25.00",
                        "pity_before": "0.0500",
                        "pity_after": "0.0600",
                        "rtp_session": "0.9800",
                        "created_at": "2025-06-01T14:23:00.000Z"
                    },
                    {
                        "id": "60f7c2e1ab12cd3f5e678902",
                        "user_id": 456,
                        "case_id": "silver_case",
                        "server_seed_id": "efgh5678",
                        "server_seed_hash": "c1a2b3c4d5e6...",
                        "server_seed_seed": "9e8d7c6b5a4f3...",
                        "client_seed": "anotherClientSeed",
                        "nonce": 7,
                        "hmac_value": "YW5vdGhlcl9oY21hX3N0cmluZw==",
                        "raw_roll": "0.8771",
                        "table_id": "table_2B",
                        "odds_version": "v1",
                        "case_tier": "standard",
                        "prize_id": None,
                        "stake": "5.0",
                        "payout": "0.0",
                        "payout_usd": "0.00",
                        "pity_before": "0.0200",
                        "pity_after": "0.0250",
                        "rtp_session": "0.5000",
                        "created_at": "2025-06-02T10:15:30.000Z"
                    }
                    # …інші записи
                ]
            }
        }
