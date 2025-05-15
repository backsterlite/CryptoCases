from decimal import Decimal
from pydantic import BaseModel
from typing import Tuple

class CaseOpenRequest(BaseModel):
    case_id: str
    client_seed: str
    nonce: int
    server_seed_id:str

class PrizeItem(BaseModel):
    coin_amount: Tuple[str,str,str]
    usd_value: str


class CaseOpenResponse(BaseModel):
    server_seed: str
    table_id: str
    odds_version: str
    prize: PrizeItem
    payout: Decimal
    fail_streak: int
    # + будь-які деталі для фронту
    
class CommitOut(BaseModel):
    server_seed_id: str
    hash: str

class RevealOut(BaseModel):
    server_seed: str
    table_id: str
    odds_version: str