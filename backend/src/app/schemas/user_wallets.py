from typing import Dict
from decimal import Decimal

from pydantic import RootModel, BaseModel


from app.models.coin import CoinMeta


class UserTokenWallet(BaseModel):
    coin: CoinMeta
    balance: Dict[str | None,Decimal] # network -> amount string
    

class UserWalletsGrouped(RootModel[Dict[str, UserTokenWallet]]):
    """
    root model: { SYMBOL: { coin, balances } }
    """
    pass