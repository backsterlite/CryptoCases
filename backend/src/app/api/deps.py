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
    Dependency factory: check role field for User.
    If mismatch — raise 403.
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Operation requires `{required_role}` role, you have `{user.role}`"
            )
        return user
    return role_checker

@lru_cache
def get_network_registry() -> NetworkRegistry:
    return NetworkRegistry(path=settings.network_registry_path)

@lru_cache
def get_external_wallet_service() -> "ExternalWalletService":   # type: ignore  # noqa: F821
    from app.services.external_wallet_service import ExternalWalletService
    return ExternalWalletService()

@lru_cache
def get_hd_wallet_service() -> "HDWalletService":  # type: ignore # noqa: F821
    from app.utils.hd_wallet import HDWalletService
    return HDWalletService(xprv=settings.HD_XPRV)