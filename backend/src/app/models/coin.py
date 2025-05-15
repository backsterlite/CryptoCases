from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_DOWN

from app.models.coin_registry import NormalizedCoin
from app.services.coin_registry import CoinRegistry



@dataclass
class Coin:
    id: str
    symbol: str
    name: str
    decimal_places: List[Optional[Dict[str, int]]] # network → decimal places
    networks: List[str] # supported networks
    _allow_direct_init: bool = False
    
    def get_precision(self, network: str) -> int:
        return self.decimal_places.get(network, 18)  # fallback = 18
    
    @classmethod
    def from_registry(cls, normalized: NormalizedCoin) -> Coin:
        return cls(
            id=normalized.coingecko_id,
            symbol=normalized.coin_symbol,
            name=normalized.coin_name,
            decimal_places={k: v.decimal_place for k, v in normalized.coin_decimals.items()},
            networks=list(normalized.coin_contract_addresses.keys()),
            _allow_direct_init=True
        )
    
    def __post_init__(self):
        if not hasattr(self, "_allow_direct_init"):
            raise RuntimeError("Use Coin.from_registry(...) to create Coin")

@dataclass
class CoinAmount:
    coin: Coin
    network: str
    amount: Decimal
    
    def get_precision(self) -> int:
        return self.coin.get_precision(self.network)

    def to_atomic(self) -> int:
        """Convert to smallest unit: 0.000001 → 1_000_000"""
        precision = self.get_precision()
        return int((self.amount * Decimal(10 ** precision)).to_integral_value(rounding=ROUND_DOWN))
    
    @classmethod
    def from_atomic(cls, coin: Coin, network: str, atomic: int) -> CoinAmount:
        """Set amount from atomic (int) value"""
        precision = coin.get_precision(network=network)
        amount = Decimal(atomic) / Decimal(10 ** precision)
        return cls(coin=coin, network=network, amount=amount)

    # def from_atomic(self, atomic: int) -> None:
    #     """Set amount from atomic (int) value"""
    #     precision = self.get_precision()
    #     self.amount = Decimal(atomic) / Decimal(10 ** precision)

    def as_display(self) -> str:
        """Return human-readable format"""
        precision = self.get_precision()
        return f"{self.amount:.{precision}f} {self.coin.symbol} ({self.network})"
    
    def to_storage(self) -> Tuple[str, str, str]:
        """Convert to (symbol, network, amount_str)"""
        return self.coin.id, self.network, str(self.amount)
    
    @classmethod
    def from_str(cls, coin_id: str, network: str, amount_str: str, coin: Optional[Coin] = None) -> "CoinAmount":
        if coin is None:
            coin = CoinRegistry.get_runtime(coin_id)
            if coin is None:
                raise ValueError(f"Unknown coin symbol: {coin_id}")
        
        precision = coin.get_precision(network)
        amount = Decimal(amount_str).quantize(Decimal("1." + "0" * precision))
        
        return cls(
            coin=coin,
            network=network,
            amount=amount
        )