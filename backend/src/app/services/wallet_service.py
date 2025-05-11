from decimal import Decimal
from typing import Dict, Optional
from app.db.models.user import User
from app.services.coin_registry import CoinRegistry


def get_balance(user: User, token: str, network: str) -> Decimal:
    try:
        raw = user.wallets[token][network]
        return Decimal(raw)
    except (KeyError, TypeError, ValueError):
        return Decimal("0")


def has_sufficient_balance(user: User, token: str, network: str, amount: Decimal) -> bool:
    return get_balance(user, token, network) >= amount


def increase(user: User, token: str, network: str, amount: Decimal):
    current = get_balance(user, token, network)
    new_amount = current + amount
    _set(user, token, network, new_amount)


def decrease(user: User, token: str, network: str, amount: Decimal):
    if not has_sufficient_balance(user, token, network, amount):
        raise ValueError("Insufficient balance")
    current = get_balance(user, token, network)
    new_amount = current - amount
    _set(user, token, network, new_amount)


def _set(user: User, token: str, network: str, amount: Decimal):
    # Normalize as string with proper decimal precision
    decimals = CoinRegistry.get_decimals(token, network) or 6
    str_value = f"{amount:.{decimals}f}"
    user.wallets.setdefault(token, {})[network] = str_value


def to_display(token: str, network: str, amount: str) -> str:
    decimals = CoinRegistry.get_decimals(token, network) or 6
    value = Decimal(amount)
    return f"{value:.{decimals}f}"