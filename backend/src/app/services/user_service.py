
from typing import Optional, Dict

from app.db.models.user import User
from app.services.coin_registry import CoinRegistry
from app.models.coin import CoinAmount
from app.config.settings import settings

class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        return await User.find_one(User.telegram_id == telegram_id)

    @staticmethod
    async def create_user(telegram_id: int) -> User:
        user = User(
            telegram_id=telegram_id,
            wallets= UserService.get_initial_wallet(),
            history=[]
        )
        await user.insert()
        return user

    @staticmethod
    async def get_or_create_user(telegram_id: int) -> User:
        existing = await UserService.get_user_by_telegram_id(telegram_id)
        if existing:
            return existing
        return await UserService.create_user(telegram_id)
    
    @staticmethod
    def get_initial_wallet() -> Dict[str,Dict[str,str]]:
        """
        Returns initial wallet structure with zero balances
        for base tokens (e.g., USDT, USDC) across all supported networks.
        """
       
        wallets: Dict[str, Dict[str, str]] = {}

        for symbol in settings.BASE_TOKENS:
            coin = CoinRegistry.get_runtime(symbol)
            if not coin:
                continue

            wallets[symbol] = {}
            for network in coin.networks:
                # створюємо CoinAmount із atomic = 0
                ca = CoinAmount.from_atomic(coin, network, 0)
                _, _, amt_str = ca.to_storage()
                wallets[symbol][network] = amt_str

        return wallets