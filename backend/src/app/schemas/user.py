from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from app.models.coin import CoinAmount
from app.schemas.user_wallets import UserWalletsGrouped



class UserCreate(BaseModel):
    telegram_id: int
    name: Optional[str] = None
    

class UserResponsePublic(BaseModel):
    telegram_id: int
    wallets: UserWalletsGrouped
    history: List[str]

    model_config = ConfigDict( from_attributes=True)
    
class UserResponsePrivate(BaseModel):
    id: Optional[str] = Field(alias="_id")
    telegram_id: int
    balance_usd: float
    wallets: List[CoinAmount]
    history: List[str]

    model_config = ConfigDict( from_attributes=True)