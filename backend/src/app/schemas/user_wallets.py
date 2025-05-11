from typing import Dict
from pydantic import RootModel, BaseModel


from app.models.coin import Coin


class UserTokenWallet(BaseModel):
    coin: Coin
    balances: Dict[str,str] # network -> amount string
    

class UserWalletsGrouped(RootModel[Dict[str, UserTokenWallet]]):
    pass