from fastapi import Depends, HTTPException
from app.core.auth_jwt import (
    oauth2_scheme,
    verify_access_token,
    )
from app.db.models.user import User
from app.services.user_service import UserService

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    telegram_id = verify_access_token(token)
    user = await UserService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user