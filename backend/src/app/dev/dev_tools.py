from fastapi import APIRouter, Query
from app.core.auth_jwt import create_access_token
from app.config.settings_test import settings
from app.services.user_service import UserService
from app.schemas.user import UserResponsePrivate, UserCreateTelegram
from app.schemas.auth import TokenResponse

router = APIRouter(prefix="/dev", tags=["Dev Tools"])

@router.get("/gen_token")
async def generate_token_for_testing(
    telegram_id: int = Query(..., description="Telegram ID to simulate login"),
    bot_token: str = Query(..., description="Dev-only bot token for security")
):
    if bot_token != settings.dev_bot_token:
        return {"error": "unauthorized"}

    token = create_access_token(data={"sub": str(telegram_id)})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/user/create", response_model=TokenResponse)
async def get_user(payload: UserCreateTelegram):
    user = await UserService.get_or_create_user(payload)
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return TokenResponse(access_token=access_token)