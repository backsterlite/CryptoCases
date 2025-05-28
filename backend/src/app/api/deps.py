from functools import lru_cache
from fastapi import Depends, HTTPException
from app.core.auth_jwt import (
    oauth2_scheme,
    verify_access_token,
    )
from app.db.models.user import User
from app.services.user_service import UserService
from app.config.network_registry import NetworkRegistry
from app.config.settings import settings



async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    telegram_id = verify_access_token(token)
    user = await UserService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@lru_cache
def get_network_registry() -> NetworkRegistry:
    return NetworkRegistry(path=settings.network_registry_path)

@lru_cache
def get_external_wallet_service() -> "ExternalWalletService":
    from app.services.external_wallet_service import ExternalWalletService
    return ExternalWalletService()

@lru_cache
def get_hd_wallet_service() -> "HDWalletService":
    from app.utils.hd_wallet import HDWalletService
    return HDWalletService(xprv=settings.HD_XPRV)