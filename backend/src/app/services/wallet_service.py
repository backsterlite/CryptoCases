from decimal import Decimal, InvalidOperation
from fastapi import HTTPException
from typing import Dict, Optional
from app.db.models.user import User
from app.config.coin_registry import CoinRegistry
from app.models.coin import CoinAmount
from pymongo import ReturnDocument

class WalletService:
    
    @staticmethod
    async def update_coin_balance(
        user_id: int,
        coin_id: str,
        network: str,
        delta_str: str
    ) -> dict:
        """
        Atomically add delta to user.wallets[symbol][network].
        If resulting amount <= 0, remove that network (and symbol if пусто).
        Returns updated dict for this symbol (or {} if removed).
        """
        # 1.  delta parsing
        try:
            delta_ca = CoinAmount.from_str(coin_id, network, delta_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid delta format")

        # 2. Find User
        user = await User.find_one(User.user_id == user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 3. current balance
        current_str = user.wallets.get(coin_id, {}).get(network, "0")
        current_ca = CoinAmount.from_str(coin_id, network, current_str)

        # 4. calculate new atomic
        new_atomic = current_ca.to_atomic() + delta_ca.to_atomic()

        # 5. Atomic update in DB
        coll = User.get_motor_collection()
        if new_atomic > 0:
            new_ca = CoinAmount.from_atomic(current_ca.coin, network, new_atomic)
            _, _, new_str = new_ca.to_storage()
            updated = await coll.find_one_and_update(
                {"user_id": user_id},
                {"$set": {f"wallets.{coin_id}.{network}": new_str}},
                return_document=ReturnDocument.AFTER
            )
        else:
            # прибрати мережу
            updated = await coll.find_one_and_update(
                {"user_id": user_id},
                {"$unset": {f"wallets.{coin_id}.{network}": ""}},
                return_document=True
            )
            # якщо під symbol більше немає мереж – прибрати coin_id
            if updated and (
                coin_id in updated.get("wallets", {}) and
                not updated["wallets"][coin_id]
            ):
                await coll.update_one(
                    {"user_id": user_id},
                    {"$unset": {f"wallets.{coin_id}": ""}}
                )

        # 6. Повернути свіжий словник мереж→amount
        fresh = (await User.find_one(User.user_id == user_id)
                 ).wallets.get(coin_id, {})
        return fresh



def get_balance(user: User, token: str, network: str) -> Decimal:
    try:
        raw = user.wallets[token][network]
        return Decimal(raw)
    except (KeyError, TypeError, ValueError):
        return Decimal("0")


def has_sufficient_balance(user: User, token: str, network: str, amount: Decimal) -> bool:
    return get_balance(user, token, network) >= amount


def to_display(token: str, network: str, amount: str) -> str:
    decimals = CoinRegistry.get_decimals(token, network) or 6
    value = Decimal(amount)
    return f"{value:.{decimals}f}"