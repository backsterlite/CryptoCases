from decimal import Decimal
from typing import Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict, RootModel

from app.config.coin_registry import CoinMeta

class UserTokenWallet(BaseModel):
    coin: CoinMeta
    balance: Dict[str | None,Decimal] # network -> amount string
    

class UserWalletsGrouped(RootModel[Dict[str, UserTokenWallet]]):
    """
    root model: { SYMBOL: { coin, balances } }
    """
    pass

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
    

#------------------------------------------------------
#swap logic
#------------------------------------------------------
class ExchangeQuoteRequest(BaseModel):
    """
    Request model for getting a quote: how much `to_token` user would receive
    for a given `from_amount`.
    """
    from_token: str = Field(..., description="Symbol of the token to swap from, e.g. 'USDT'")
    from_network: str | None = Field(
        None, description="Network of the token to swap from, e.g. 'ERC20'. Use None if network-agnostic."
    )
    to_token: str = Field(..., description="Symbol of the token to swap to, e.g. 'USDC'")
    to_network: str | None = Field(
        None, description="Network of the token to swap to, e.g. 'ERC20'. Use None if network-agnostic."
    )
    from_amount: Decimal = Field(..., description="Amount of `from_token` user wants to spend")

    model_config = ConfigDict(
        validate_default=True,
        extra="forbid",
    )

    @field_validator("from_amount")
    @classmethod
    def check_positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("`from_amount` must be strictly positive")
        return v

    @field_validator("from_token", "to_token", mode="before")
    @classmethod
    def uppercase_tokens(cls, v: str) -> str:
        return v.strip().upper()
    
    @field_validator("from_network", "to_network", mode="before")
    @classmethod
    def network_value_transform(cls, net: str) -> str | None:
        if net == 'None':
            return None
        return net


class ExchangeQuoteResponse(BaseModel):
    """
    Response model when user requests a quote; no balance changes yet.
    """
    from_token:      str     = Field(..., description="Uppercase symbol of the token to swap from")
    from_network:    str | None = Field(..., description="Uppercase network of the token to swap from")
    to_token:        str     = Field(..., description="Uppercase symbol of the token to swap to")
    to_network:      str | None = Field(..., description="Uppercase network of the token to swap to")
    to_amount:     Decimal = Field(..., description="Amount of `from_token` to be spent")


class ExchangeExecuteRequest(BaseModel):
    """
    Request model for executing the actual exchange: moves balances.
    """
    from_token:   str     = Field(..., description="Symbol to swap from (uppercase)")
    from_network: str | None = Field(..., description="Network to swap from (uppercase or None)")
    to_token:     str     = Field(..., description="Symbol to swap to (uppercase)")
    to_network:   str | None = Field(..., description="Network to swap to (uppercase or None)")
    from_amount:  Decimal = Field(..., description="Exact amount of `from_token` to debit")

    model_config = ConfigDict(
        validate_default=True,
        extra="forbid",
    )

    @field_validator("from_amount")
    @classmethod
    def validate_positive_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("`from_amount` must be strictly positive")
        return v

    @field_validator("from_token", "to_token", mode="before")
    @classmethod
    def uppercase_symbols(cls, v: str) -> str:
        return v.strip().upper()
    
    @field_validator("from_network", "to_network", mode="before")
    @classmethod
    def network_value_transform(cls, net: str) -> str | None:
        if net == 'None':
            return None
        return net


class ExchangeExecuteResponse(BaseModel):
    """
    Response after performing the exchange: confirms actual debited/credited amounts
    and returns it's
    """
    from_amount:     Decimal                   = Field(..., description="Amount debited of `from_token`")
    to_amount:       Decimal                   = Field(..., description="Amount credited of `to_token`")
    