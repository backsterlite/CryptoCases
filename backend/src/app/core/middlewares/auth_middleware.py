from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config.settings import get_settings
from app.core.config.settings import Settings
from app.core.config.auth import verify_telegram_auth



class TelegramAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next):
        settings: Settings = get_settings()
        init_data = request.query_params.get("init_data")
        if not init_data:
            raise HTTPException(status_code=401, detail="Missing init_data")

        telegram_id = verify_telegram_auth(init_data, settings.bot_token)
        request.state.telegram_id = telegram_id
        return await call_next(request)
