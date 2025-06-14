from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class NetworkListResponse(BaseModel):
    networks: List[str]



class GenerateAddressRequest(BaseModel):
    network: str = Field(..., description="Network code, e.g. 'ton'")
    token: str = Field(..., description="Token symbol, default native coin")
    wallet_type: str = Field(..., description="'manual' or 'telegram'")

class GenerateAddressResponse(BaseModel):
    external_wallet_id: str = Field(..., description="ID of the ExternalWallet record")
    address: str = Field(..., description="Deposit address for user")
    qr_code_url: Optional[str] = Field(None, description="QR code image URL for easy scanning")
    min_amount: Decimal = Field(..., description="Minimum deposit amount required to cover deployment/gas fees")