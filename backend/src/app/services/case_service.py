import random

from decimal import Decimal
from typing import Dict

from app.db.models.user import User
from app.services.wallet_service import has_sufficient_balance, decrease, increase
from app.db.models.case_log import CaseLog

# Фіксовані кейси MVP
CASES = {
    "basic": {
        "price": Decimal("5.0"),
        "token": "USDT",
        "network": "TRC20"
    },
    "pro": {
        "price": Decimal("10.0"),
        "token": "USDT",
        "network": "TRC20"
    },
    "vip": {
        "price": Decimal("20.0"),
        "token": "USDT",
        "network": "TRC20"
    },
}

# Пул виграшів (токен, ймовірність, мін/макс сума)
REWARDS = [
    ("DOGE", 0.4, Decimal("1"), Decimal("10")),
    ("SHIB", 0.3, Decimal("1000"), Decimal("10000")),
    ("PEPE", 0.2, Decimal("100000"), Decimal("500000")),
    ("USDT", 0.1, Decimal("1"), Decimal("5"))
]


async def open_case(user: User, case_id: str) -> Dict[str,str]:
    case = CASES.get(case_id)
    if not case:
        raise ValueError("Invalid case ID")

    token = case["token"]
    network = case["network"]
    price = case["price"]

    if not has_sufficient_balance(user, token, network, price):
        raise ValueError("Insufficient balance to open case")

    # Списуємо вартість кейсу
    decrease(user, token, network, price)

    # Випадковий виграш
    coins, weights, mins, maxs = zip(*REWARDS)
    reward_token = random.choices(coins, weights=weights, k=1)[0]
    reward_config = next(item for item in REWARDS if item[0] == reward_token)
    amount = Decimal(str(round(random.uniform(float(reward_config[2]), float(reward_config[3])), 4)))

    # На цей етап — просто видаємо в тій самій мережі TRC20 (можна ускладнити пізніше)
    increase(user, reward_token, network, amount)
    
    log = CaseLog(
        user_id=user.id,
        case_id=case_id,
        token=reward_token,
        network=network,
        amount=str(amount)
    )
    await log.insert()
    

    return {
        "token": reward_token,
        "network": network,
        "amount": str(amount)
    }