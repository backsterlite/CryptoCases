from decimal import Decimal
from datetime import datetime, timezone
from beanie import Document
from pydantic import BaseModel, Field
from typing import List

class RewardItem(BaseModel):
    coin_id: str
    amount: str
    network: str
    sub_chance: Decimal

class TierConfig(BaseModel):
    name: str
    chance: Decimal
    rewards: List[RewardItem]
    
    
    
class OddsVersion(BaseModel):
    version: str
    sha256: str
    url: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))    

class CaseConfig(Document):
    """
    A collection of cases with data on the cost and versions of odds files.
    """
    case_id: str = Field(..., description="case UUID")
    price_usd: Decimal = Field(..., description="Case opening price in USDT")
    tiers: List[TierConfig]
    pity_after: int
    pity_bonus_tier: str
    global_pool_usd: Decimal
    pool_reset_interval: str
    # Нове поле для цільового EV
    ev_target: Decimal = Field(default=Decimal("0.5"), description="House Edge EV")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    odds_versions: List[OddsVersion] = Field(
        description="config version for chance file, update when tiers change or sub_chance"
    )

    class Settings:
        name = "case_configs"
        indexes = ["case_id"]