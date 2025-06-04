
from typing import Optional, Dict

from app.db.models.user import User
from app.services.wallet_service import WalletService
from app.schemas.user import UserCreateTelegram



class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        return await User.find_one(User.user_id == telegram_id)

    @staticmethod
    async def create_user(data: UserCreateTelegram) -> User:
        await WalletService.initial_wallets(int(data.telegram_id))
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
    
