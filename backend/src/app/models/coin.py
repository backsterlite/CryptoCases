from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from decimal import Decimal, ROUND_DOWN, localcontext

from app.models.coin_registry import NormalizedCoin
from src.app.config.coin_registry import CoinRegistry

TARGET_SCALE = Decimal("0.000001")

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
    def from_id(cls, coin_id: str) -> Coin:
        coin = CoinRegistry.get_runtime(coin_id)
        if coin is None:
            raise ValueError(f"Unknown coin symbol: {coin_id}")
        return coin
    
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
    @staticmethod
    def _needed_prec(a: Decimal, b: Decimal, reserve: int = 4) -> int:
        """How many significant figures are needed so that nothing is cut off when multiplying"""
        digits_a = len(a.normalize().as_tuple().digits)
        digits_b = len(b.normalize().as_tuple().digits)
        return digits_a + digits_b + reserve    # a little bit of spare money so you don't have to worry about moving
    
    
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
            coin = Coin.from_id(coin_id=coin_id)
        
        precision = coin.get_precision(network)
        amount = Decimal(amount_str).quantize(Decimal("1." + "0" * precision))
        
        return cls(
            coin=coin,
            network=network,
            amount=amount
        )
    
    @classmethod
    def amount_from_usd(cls, coin_id: str, network: str, value_in_usd: Decimal, rate: Decimal) -> Decimal:
        coin: Coin = CoinRegistry.get_runtime(coin_id=coin_id)
        amount = value_in_usd / rate
        prec = coin.get_precision(network=network)
        return amount.quantize(prec)
    
    def to_usd(self, rate: Decimal, out_scale: Decimal = TARGET_SCALE) -> Decimal:
        prec = CoinAmount._needed_prec(self.amount, rate)

        with localcontext() as ctx:
            ctx.prec = prec
            usd = self.amount * rate

        return usd.quantize(out_scale)