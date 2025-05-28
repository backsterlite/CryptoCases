
from typing import Optional, Dict

from app.db.models.user import User
from app.db.models.internal_balance import InternalBalance
from app.config.coin_registry import CoinRegistry
from app.config.settings import settings
from app.models.coin import CoinAmount
from app.schemas.user import UserCreateTelegram



class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        return await User.find_one(User.user_id == telegram_id)

    @staticmethod
    async def create_user(data: UserCreateTelegram) -> User:
        await UserService.initial_wallets(int(data.telegram_id))
        user = User(
            user_id=int(data.telegram_id),
            first_name=data.first_name,
            last_name=data.last_name,
            user_name=data.username
        )
        await user.insert()
        return user

    @staticmethod
    async def get_or_create_user(data: UserCreateTelegram) -> User:
        existing = await UserService.get_user_by_telegram_id(data.telegram_id)
        if existing:
            return existing
        return await UserService.create_user(data)
    
    @staticmethod
    async def initial_wallets(user_id: int) -> None:
        """
        Returns initial wallet structure with zero balances
        for base tokens (e.g., USDT, USDC) across all supported networks.
        """

        for symbol in settings.BASE_TOKENS:
            coin = CoinRegistry.get_runtime(symbol)
            if not coin:
                continue

            for network in coin.networks:
                # створюємо CoinAmount із atomic = 0
                ca = CoinAmount.from_atomic(coin, network, 0)
                _, _, amt_str = ca.to_storage()
                new_balance = InternalBalance(
                    user_id=user_id,
                    coin=ca.coin.id,
                    network=ca.network,
                    balance=ca.amount
                )
                await new_balance.insert()