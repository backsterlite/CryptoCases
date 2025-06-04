from decimal import Decimal
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field


class RewardItem(BaseModel):
    coin_id: str
    amount: Decimal
    network: str | None
    sub_chance: Decimal

class TierConfig(BaseModel):
    name: str
    chance: Decimal
    rewards: List[RewardItem]
    
    
    
class OddsVersion(BaseModel):
    version: str = Field(default="", description="Unique version odd table e.g. datetime of create")
    sha256: str = Field(default="", description="Hash sum file with table")
    url: str = Field(default="", description="Link to file with table [optional]")
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))    