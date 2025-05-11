from decimal import Decimal
from typing import Dict
from pydantic import BaseModel, Field

class WithdrawalRequest(BaseModel):
    token: str = Field(..., description="Token symbol, e.g. USDT")
    network: str = Field(..., description="Network code, e.g. ERC20")
    amount: Decimal = Field(..., description="Amount to withdraw")
    address: str = Field(..., description="Destination address")

class AdjustRequest(BaseModel):
    symbol: str = Field(..., description="Token symbol, e.g. USDT")
    network: str = Field(..., description="Network code, e.g. ERC20")
    delta: str   = Field(..., description="Change amount as Decimal string (can be negative)")

class WalletResponse(BaseModel):
    balances: Dict[str, str]  # network → updated amount as string