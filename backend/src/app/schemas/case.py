from decimal import Decimal
from pydantic import BaseModel
from typing import Tuple, List, Optional

from beanie import PydanticObjectId

class CaseOpenRequest(BaseModel):
    case_id: str
    client_seed: str
    nonce: int
    server_seed_id:str

class PrizeItem(BaseModel):
    coin_amount: Tuple[str,str,Decimal]
    usd_value: str
    reward_tier: str


class CaseOpenResponse(BaseModel):
    server_seed: str
    table_id: str
    odds_version: str
    prize: PrizeItem
    payout: Decimal
    fail_streak: int
    spin_log_id: Optional[PydanticObjectId] = None
    # + будь-які деталі для фронту
    
class CommitOut(BaseModel):
    server_seed_id: str
    hash: str

class RevealOut(BaseModel):
    server_seed: str
    table_id: str
    odds_version: str

class RewardOut(BaseModel):
    coin_id: str
    amount: Decimal
    network: str
    sub_chance: Decimal

class TierOut(BaseModel):
    name: str
    chance: Decimal
    rewards: List[RewardOut]

class CaseOut(BaseModel):
    case_id: str
    price_usd: Decimal
    tiers: List[TierOut]
    pity_after: int
    pity_bonus_tier: str
    global_pool_usd: Decimal
    ev_target: Decimal
    nonce: Optional[int] = 0
    # додайте інші поля за потреби