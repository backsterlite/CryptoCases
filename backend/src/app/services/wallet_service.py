from decimal import Decimal, InvalidOperation
from typing import Dict, Optional, Any

from fastapi import HTTPException, status
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorClientSession

from app.db.models.user import User

from app.models.coin import CoinAmount, Coin
from app.db.models.internal_balance import InternalBalance


class WalletService:
    

    @staticmethod
    async def get_balance(user: User, token: str, network: str) -> Decimal:
        """
        Retrieve the balance for a given user, token and network.
        If no wallet is found, return Decimal('0').
        """
        wallet = await InternalBalance.find_one(
            InternalBalance.user_id==user.id,
            InternalBalance.coin==token,
            InternalBalance.network==network
        )
        if wallet is None:
            return Decimal("0")
        return wallet.balance
    

    @staticmethod
    async def has_sufficient_balance(user: User, token: str, network: str, amount: Decimal) -> bool:
        current_balance = await WalletService.get_balance(user, token, network)
        return  current_balance >= amount


    @staticmethod
    async def initial_wallets(
        user_id: int,
        session: AsyncIOMotorClientSession | None) -> None:
        """
        Returns initial wallet structure with zero balances
        for base tokens (e.g., USDT, USDC) across all supported networks.
        """
        from app.core.config.settings import Settings
        from app.core.config.settings import get_settings
        
        settings: Settings = get_settings()
                
        for symbol in settings.BASE_TOKENS:
            await InternalBalance.insert_one(
                    InternalBalance(
                    user_id=user_id,
                    coin=symbol,
                    network=None,
                    balance=Decimal("0")
                    ),
                    session=session
                )