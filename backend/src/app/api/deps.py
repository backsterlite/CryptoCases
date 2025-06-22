# backend/src/app/api/deps.py
from functools import lru_cache
from typing import Annotated, Optional
import logging

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.auth_jwt import JWTManager
from app.db.models.user import User
from app.services.user_service import UserService
from app.core.config.network_registry import NetworkRegistry
from app.core.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Використовуємо HTTPBearer замість OAuth2PasswordBearer для кращої безпеки
security = HTTPBearer(auto_error=False)

class SecurityDependencies:
    """Клас для управління залежностями безпеки"""
    
    @staticmethod
    def get_token_payload(
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> dict:
        """
        Отримання та валідація JWT токена з заголовків
        """
        if not credentials or not credentials.credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        client_ip = request.client.host if request.client else "unknown"
        
        try:
            payload = JWTManager.verify_access_token(token)
            
            # Додаткові перевірки безпеки
            if payload.get("token_type") != "access":
                raise ValueError("Invalid token type")
            
            # Логування для аудиту
            logger.debug(
                f"Token validated for user {payload.get('sub')} from IP {client_ip}"
            )
            
            return payload
            
        except ValueError as e:
            logger.warning(
                f"Token validation failed from IP {client_ip}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(
                f"Token validation error from IP {client_ip}: {e}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    @staticmethod
    async def get_current_user(
        request: Request,
        token_payload: dict = Depends(get_token_payload)
    ) -> User:
        """
        Отримання поточного користувача з токена
        """
        try:
            user_id_str = token_payload.get("sub")
            if not user_id_str or not user_id_str.isdigit():
                raise ValueError("Invalid user ID in token")
            
            user_id = int(user_id_str)
            user = await UserService.get_user_by_telegram_id(user_id)
            
            if not user:
                logger.warning(f"User {user_id} not found in database")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Перевірка активності користувача (якщо потрібно)
            if hasattr(user, 'is_active') and not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is disabled"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User authentication failed"
            )

def require_role(required_role: str):
    """
    Dependency factory: перевірка ролі користувача з покращеною безпекою
    """
    async def role_checker(
        request: Request,
        user: User = Depends(SecurityDependencies.get_current_user),
        token_payload: dict = Depends(SecurityDependencies.get_token_payload),
        settings: Settings = Depends(get_settings)
    ) -> User:
        
        # Перевірка ролі з токена (додаткова безпека)
        token_role = token_payload.get("scope", "")
        if token_role != user.role:
            logger.warning(
                f"Role mismatch for user {user.user_id}: "
                f"token={token_role}, db={user.role}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token role mismatch"
            )
        
        # Перевірка пріоритету ролей
        user_priority = settings.ROLE_PRIORITIES.get(user.role)
        required_priority = settings.ROLE_PRIORITIES.get(required_role)

        if user_priority is None:
            logger.error(f"Unknown user role: {user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Invalid user role: {user.role}"
            )

        if required_priority is None:
            logger.error(f"Unknown required role: {required_role}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server configuration error"
            )

        if user_priority < required_priority:
            client_ip = request.client.host if request.client else "unknown"
            logger.warning(
                f"Access denied for user {user.user_id} (role: {user.role}) "
                f"to {required_role} resource from IP {client_ip}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return user

    return role_checker

# Часто використовувані залежності
get_token_payload = SecurityDependencies.get_token_payload
get_current_user = SecurityDependencies.get_current_user

# Швидкі ролі для зручності
require_user = require_role("user")
require_admin = require_role("admin")
require_worker = require_role("worker")

# Опціональна автентифікація (не викидає помилку якщо токен відсутній)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    Опціональна автентифікація - повертає користувача якщо токен валідний,
    None якщо токен відсутній
    """
    if not credentials:
        return None
    
    try:
        payload = JWTManager.verify_access_token(credentials.credentials)
        user_id = int(payload.get("sub", 0))
        return await UserService.get_user_by_telegram_id(user_id)
    except Exception:
        return None

# Інші залежності (без змін)
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