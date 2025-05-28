from datetime import datetime, timezone

from beanie import Document
from pymongo import IndexModel, ASCENDING
from pydantic import Field
from decimal import Decimal



class InternalBalance(Document):
    user_id: int = Field(..., description="User identifier")
    coin: str = Field(..., description="Asset id")
    network: str = Field(..., description="Asset network")
    balance: Decimal = Field(default=Decimal('0'), description="User's internal balance")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Settings:
        name = "internal_balances"
        indexes = [
            IndexModel(  [("user_id", ASCENDING), ("coin", ASCENDING), ("network", ASCENDING)],
                name="unique_user_coin_network",
                unique=True)
        ]