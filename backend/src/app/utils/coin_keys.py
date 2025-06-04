# src/app/utils/coin_keys.py
from app.config.coin_registry import CoinRegistry

def to_id(value: str) -> str:
    """Завжди повертає coingecko_id у lower-case (ключ для БД, rate-cache)."""
    meta = CoinRegistry.get(value)
    return meta.coingecko_id.lower() if meta else value.lower()

def to_symbol(value: str) -> str:
    """Завжди повертає canonical symbol у UPPER-CASE (для реєстрів)."""
    meta = CoinRegistry.get(value)
    return meta.symbol.upper() if meta else value.upper()
