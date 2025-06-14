from decimal import Decimal

from pydantic import BaseModel, Field

class WithdrawalRequest(BaseModel):
    network: str = Field(..., description="Network code, e.g. 'ton'")
    token: str = Field(..., description="Token symbol for withdrawal, e.g. 'USDT'")
    amount: Decimal = Field(..., description="Amount to withdraw in token units")
    to_address: str = Field(..., description="Destination address for withdrawal")

class WithdrawalResponse(BaseModel):
    withdrawal_id: str = Field(..., description="ID of the created withdrawal request")
    status: str = Field(..., description="Initial status, e.g. 'pending'")