from pydantic import BaseModel
from decimal import Decimal

class WithdrawalRequest(BaseModel):
    token: str
    network: str
    amount: Decimal
    address: str