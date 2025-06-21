import json

from fastapi import APIRouter, HTTPException, status, Request, Depends
from slowapi import Limiter

from app.core.auth import verify_telegram_auth
from app.core import auth_jwt

from app.schemas.auth import TelegramAuthRequest, TokenResponse, RefreshRequest
from app.schemas.user import parse_telegram_init
from app.services.user_service import UserService
from app.core.config.settings import Settings
from app.core.api_limiter import limiter
from app.core.config.settings import get_settings
from . import API_V1

router = APIRouter(prefix=f"{API_V1}/auth", tags=["Auth"])



@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("5/minute")
async def refresh_token(request: Request, data: RefreshRequest):
    try:
        access_token, refresh_token = await auth_jwt.verify_and_rotate_refresh_token(data.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/telegram", response_model=TokenResponse)
@limiter.limit("5/minute")
async def auth_telegram(
    request: Request,
    data: TelegramAuthRequest,
    settings: Settings = Depends(get_settings)
    ):
    print(data)
    raw_data = verify_telegram_auth(data.init_data, settings.bot_token)
    try:
        user_data = parse_telegram_init(raw_data)
        user = await UserService.get_or_create_user(user_data)
        assert user is not None
        access = auth_jwt.create_access_token(data={"sub": str(user.user_id)}, role=user.role)
        refresh = await auth_jwt.create_refresh_token(str(user.user_id))
        return TokenResponse(access_token=access, refresh_token=refresh)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=str(e))