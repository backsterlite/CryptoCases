from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class NetworkListResponse(BaseModel):
    networks: List[str]

class TokenInfo(BaseModel):
    symbol: str
    decimals: int

class TokenListResponse(BaseModel):
    network: str
    tokens: List[TokenInfo]

class GenerateAddressRequest(BaseModel):
    network: str
    token: str
    wallet_type: Optional[str] = "onchain"

class GenerateAddressResponse(BaseModel):
    external_wallet_id: str
    address: str
    qr_code_url: Optional[str] = None

class DepositHistoryItem(BaseModel):
    id: str
    network: str
    token: str
    address: str
    amount: Decimal
    status: str
    tx_hash: Optional[str]
    created_at: datetime

class DepositHistoryResponse(BaseModel):
    history: List[DepositHistoryItem]