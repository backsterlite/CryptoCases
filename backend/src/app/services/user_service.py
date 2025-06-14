
from typing import Optional, Dict

from app.db.models.user import User
from app.services.wallet_service import WalletService
from app.schemas.user import UserCreateTelegram
from app.db.transaction import TransactionManager



class UserService:
    @staticmethod
    async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        return await User.find_one(User.user_id == telegram_id)

    @staticmethod
    async def create_user(data: UserCreateTelegram) -> User | None:
        tx = TransactionManager()
        async with tx() as session:
            user = await User.insert_one(User(
                            user_id=int(data.telegram_id),
                            first_name=data.first_name,
                            last_name=data.last_name,
                            user_name=data.username
                            ),
                            session=session
                        )
            await WalletService.initial_wallets(
                user_id=int(data.telegram_id),
                session=session
                )
       
        return user

    @staticmethod
    async def get_or_create_user(data: UserCreateTelegram) -> User | None:
        existing = await UserService.get_user_by_telegram_id(data.telegram_id)
        if existing:
            return existing
        return await UserService.create_user(data)
    
