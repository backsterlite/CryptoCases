
from typing import Optional, Dict

from app.db.models.user import User
from app.services.coin_registry import CoinRegistry

class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        return await User.find_one(User.telegram_id == telegram_id)

    @staticmethod
    async def create_user(telegram_id: int) -> User:
        user = User(
            telegram_id=telegram_id,
            balance_usd=0.0,
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
        base_tokens = ["TETHER", "USDC"]  # Extend if needed later
        wallets = {}

        for symbol in base_tokens:
            coin = CoinRegistry.get_runtime(symbol)
            print(f"COIN: {coin}")
            if not coin:
                raise ValueError(f"COIN: {coin}, registry: {CoinRegistry._registry}")  #TODO change to custom error
            wallets[symbol] = {}
            for network_code in coin.networks:
                wallets[symbol][network_code] = f"0.{"0"*coin.get_precision(network_code)}"
        
        return wallets