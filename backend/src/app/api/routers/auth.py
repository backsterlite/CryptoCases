# backend/src/app/api/routers/auth.py
import json
import logging
from typing import Optional
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Request,
    Depends,
    Header
)

from app.core.auth import TelegramAuthValidator
from app.core.auth_jwt import JWTManager, verify_access_token
from app.schemas.auth import (
    TokenResponse,
    RefreshRequest,
    TelegramAuthRequestSecure,
    LogoutRequest,
    TokenInfo
    )
from app.schemas.user import parse_telegram_init
from app.services.user_service import UserService
from app.core.config.settings import Settings, get_settings
from app.core.api_limiter import limiter
from app.api.deps import require_role
from . import API_V1

logger = logging.getLogger(__name__)
router = APIRouter(prefix=f"{API_V1}/auth", tags=["Auth"])




@router.post("/telegram", response_model=TokenResponse)
@limiter.limit("3/minute")  # Зменшили ліміт для безпеки
async def auth_telegram(
    request: Request,
    data: TelegramAuthRequestSecure,
    settings: Settings = Depends(get_settings)
):
    """
    Авторизація через Telegram WebApp з повною валідацією
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        # 1. Валідація Telegram init_data
        auth_data = TelegramAuthValidator.verify_telegram_auth(
            data.init_data, 
            settings.bot_token
        )
        
        # 2. Парсинг даних користувача
        user_data = parse_telegram_init({
            "user": json.dumps(auth_data.user),
            "auth_date": str(auth_data.auth_date),
            "query_id": auth_data.query_id
        })
        
        # 3. Створення або отримання користувача
        user = await UserService.get_or_create_user(user_data)
        if not user:
            logger.error(f"Failed to create/get user for telegram_id: {user_data.telegram_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User creation failed"
            )
        
        # 4. Створення токенів
        access_token = JWTManager.create_access_token(
            user_id=user.user_id,
            role=user.role,
            additional_claims={
                "auth_method": "telegram",
                "client_ip": client_ip
            }
        )
        
        refresh_token = await JWTManager.create_refresh_token(user.user_id)
        
        logger.info(
            f"Successful Telegram auth for user {user.user_id} "
            f"from IP {client_ip}"
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        # Перехоплюємо наші власні HTTP помилки
        raise
        
    except Exception as e:
        logger.error(
            f"Telegram auth failed for IP {client_ip}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authentication failed"
        )

@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_token(
    request: Request,
    data: RefreshRequest
):
    """
    Оновлення access токена через refresh токен
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        access_token, refresh_token = await JWTManager.verify_and_rotate_refresh_token(
            data.refresh_token
        )
        
        logger.info(f"Token refreshed from IP {client_ip}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        
    except ValueError as e:
        logger.warning(f"Refresh token validation failed from IP {client_ip}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error from IP {client_ip}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
@limiter.limit("5/minute")
async def logout(
    request: Request,
    data: LogoutRequest,
    current_user=Depends(require_role("user"))
):
    """
    Логаут з відкликанням refresh токенів
    """
    client_ip = request.client.host if request.client else "unknown"
    
    try:
        if data.revoke_all:
            # Відкликаємо всі refresh токени користувача
            success = await JWTManager.revoke_all_refresh_tokens(current_user.user_id)
        else:
            # Відкликаємо тільки поточний токен
            # Для цього потрібно передати JTI з поточного refresh токена
            # Це можна реалізувати через додатковий параметр
            success = True
        
        if success:
            logger.info(
                f"User {current_user.user_id} logged out from IP {client_ip} "
                f"(revoke_all: {data.revoke_all})"
            )
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Logout failed"
            )
            
    except Exception as e:
        logger.error(f"Logout error for user {current_user.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/token-info", response_model=TokenInfo)
async def get_token_info(
    current_user=Depends(require_role("user")),
    token_payload: dict = Depends(verify_access_token)
):
    """
    Отримання інформації про поточний токен
    """
    return TokenInfo(
        user_id=current_user.user_id,
        role=current_user.role,
        expires_at=datetime.fromtimestamp(
            token_payload["exp"], 
            tz=timezone.utc
        ).isoformat(),
        token_type="access"
    )

@router.post("/verify")
@limiter.limit("20/minute")
async def verify_token(
    request: Request,
    authorization: str = Header(..., description="Bearer token")
):
    """
    Верифікація токена (для інших сервісів)
    """
    try:
        if not authorization.startswith("Bearer "):
            raise ValueError("Invalid authorization header format")
        
        token = authorization.split(" ")[1]
        payload = JWTManager.verify_access_token(token)
        
        return {
            "valid": True,
            "user_id": int(payload["sub"]),
            "role": payload["scope"],
            "expires_at": payload["exp"]
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

# Імпор