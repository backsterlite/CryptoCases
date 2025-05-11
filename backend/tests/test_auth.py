import urllib.parse
import hmac
import hashlib
import pytest

from datetime import timedelta
from jose import JWTError
from httpx import AsyncClient

from app.main import app
from app.db.models.user import User
from app.core.auth_jwt import create_access_token, verify_access_token,  get_current_user
from app.services.user_service import UserService
from app.config.settings import settings



@pytest.mark.asyncio
class TestJWTAuth:

    async def test_create_and_verify_access_token(self):
        telegram_id = 123456
        token = create_access_token(data={"sub": str(telegram_id)}, expires_delta=timedelta(minutes=5))

        decoded_id = verify_access_token(token)
        assert decoded_id == telegram_id

    async def test_invalid_token(self):
        with pytest.raises(JWTError):
            verify_access_token("invalid.token.value")
  
            
@pytest.mark.asyncio
class TestTelegramAuthRoute:

    def generate_valid_init_data(self, telegram_id: int):
        # Приклад генерації дійсного init_data, як робить Telegram
        data = {
            "user[id]": str(telegram_id),
            "user[username]": "testuser"
        }
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        secret = hashlib.sha256(settings.bot_token.encode()).digest()
        hash = hmac.new(secret, data_check_string.encode(), hashlib.sha256).hexdigest()
        data["hash"] = hash
        return urllib.parse.urlencode(data)

    async def test_auth_telegram_success(self):
        telegram_id = 789123
        init_data = self.generate_valid_init_data(telegram_id)

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/telegram", json={"init_data": init_data})

        assert response.status_code == 200
        json_data = response.json()
        assert "access_token" in json_data
        assert json_data["token_type"] == "bearer"


@pytest.mark.asyncio
class TestGetCurrentUser:

    @pytest.fixture
    async def token_and_user(self):
        telegram_id = 999111
        user = await UserService.get_or_create_user(telegram_id)
        token = create_access_token({"sub": str(user.telegram_id)})
        return token, user

    async def test_get_current_user_from_token(self, token_and_user):
        token, user = token_and_user

        # Симулюємо Depends у роуті
        retrieved_user = await get_current_user(token=token)

        assert retrieved_user.telegram_id == user.telegram_id
        assert isinstance(retrieved_user, User)