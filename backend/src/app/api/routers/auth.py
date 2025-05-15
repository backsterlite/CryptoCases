from fastapi import APIRouter

from app.core.auth import verify_telegram_auth
from app.core.auth_jwt import create_access_token

from app.schemas.auth import TelegramAuthRequest, TokenResponse
from app.services.user_service import UserService
from app.config.settings import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/telegram", response_model=TokenResponse)
async def auth_telegram(data: TelegramAuthRequest):
    telegram_id = verify_telegram_auth(data.init_data, settings.bot_token)
    user = await UserService.get_or_create_user(telegram_id)
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return TokenResponse(access_token=access_token)