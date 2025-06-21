from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from app.core.auth_jwt import (
    oauth2_scheme,
    verify_access_token,
    )
from app.db.models.user import User
from app.services.user_service import UserService
from app.core.config.network_registry import NetworkRegistry
from app.core.config.settings import Settings
from app.core.config.settings import get_settings



async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        
        payload = verify_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Missing subject in token")
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    user = await UserService.get_user_by_telegram_id(int(user_id))
    if not user:
            raise HTTPException(status_code=404, detail="User not found")
    return user

def require_role(required_role: str):
    """
    Dependency factory: ensures that current user has at least the `required_role` level.
    Role hierarchy is defined in ROLE_PRIORITIES, where higher value => більше прав.
    If user's role priority < required_role priority, raise 403.
    """
    async def role_checker(
        user: User = Depends(get_current_user),
        settings: Settings = Depends(get_settings)
        ) -> User:
        user_priority = settings.ROLE_PRIORITIES.get(user.role)
        required_priority = settings.ROLE_PRIORITIES.get(required_role)

        if user_priority is None:
            # Невідома роль у базі – трактуємо як найнижчий рівень доступу
            raise HTTPException(
                status_code=403,
                detail=f"Unrecognized role `{user.role}`"
            )

        if required_priority is None:
            # Якщо некоректно вказана required_role в коді, можна сигналізувати помилку на боці розробника
            raise HTTPException(
                status_code=500,
                detail=f"Server misconfiguration: unknown required_role `{required_role}`"
            )

        if user_priority < required_priority:
            raise HTTPException(
                status_code=403,
                detail=(
                    f"Operation requires role `{required_role}` or higher; "
                    f"you have `{user.role}`"
                )
            )
        return user

    return role_checker



@lru_cache
def get_network_registry(settings: Settings = Depends(get_settings)) -> NetworkRegistry:
    return NetworkRegistry(path=settings.network_registry_path)

@lru_cache
def get_external_wallet_service() -> "ExternalWalletService":   # type: ignore  # noqa: F821
    from app.services.external_wallet_service import ExternalWalletService
    return ExternalWalletService()

@lru_cache
def get_deposit_service():
    from app.services.deposit_service import DepositService
    return DepositService()

@lru_cache
def get_hd_wallet_service(settings: Settings = Depends(get_settings)) -> "HDWalletService":  # type: ignore # noqa: F821
    from app.utils.hd_wallet import HDWalletService
    return HDWalletService(xprv=settings.HD_XPRV, mnemonic="")

@lru_cache
def get_blockchain_factory() -> "BlockchainClientFactory":  # type: ignore # noqa: F821
    from app.services.blockchain.factory import BlockchainClientFactory
    registry = get_network_registry()
    return BlockchainClientFactory(registry)