import json

from fastapi import APIRouter, HTTPException, status

from app.core.auth import verify_telegram_auth
from app.core import auth_jwt

from app.schemas.auth import TelegramAuthRequest, TokenResponse, RefreshRequest
from app.schemas.user import parse_telegram_init
from app.services.user_service import UserService
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/refresh")
async def refresh_token(data: RefreshRequest):
    try:
        access_token, refresh_token = await auth_jwt.verify_and_rotate_refresh_token(data.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(data: TelegramAuthRequest):
    raw_data = verify_telegram_auth(data.init_data, settings.bot_token)
    try:
        user_data = parse_telegram_init(raw_data)
        user = await UserService.get_or_create_user(user_data)
        access = auth_jwt.create_access_token(data={"sub": str(user.user_id)}, role=user.role)
        refresh = auth_jwt.create_refresh_token(str(user.user_id))
        return TokenResponse(access_token=access, refresh_token=refresh)
    except (ValueError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=400, detail=str(e))