# tests/test_authentication.py

import pytest
import urllib.parse
import hmac
import hashlib
import json
from time import time

from src.app.core.config.settings_test import settings as test_settings
from src.app.core.auth_jwt import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_and_rotate_refresh_token,
)
from src.app.services.user_service import UserService
from src.app.api.deps import get_current_user


def gen_init_data(telegram_id: int) -> str:
    """
    Генерує коректний init_data як від Telegram WebApp,
    використовуючи test_settings.bot_token.
    """
    bot_token = "7539927048:AAHyBgJNV4XWGO4MihDQ1op7wYolx3CnazA"  # Замініть на реальний токен
    user_data = {
        "id": telegram_id,
        "first_name": "Ivan",
        "last_name": "Yarmoliuk",
        "username": "backster",
        "language_code": "en"
    }
    auth_date = int(time())
    date_str = str(auth_date)
    query_id = hashlib.sha1(date_str.encode()).hexdigest()


    # Крок 1: Створення data_check_string
    data_check_string = f"auth_date={auth_date}\nquery_id={query_id}\nuser={json.dumps(user_data)}"

    # Крок 2: Генерація секретного ключа
    secret_key = hashlib.sha256(bot_token.encode()).digest()

    # Крок 3: Обчислення хешу
    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Крок 4: Формування initData
    initData = f"query_id={query_id}&user={json.dumps(user_data)}&auth_date={auth_date}&hash={computed_hash}"
    return initData


@pytest.mark.asyncio
class TestAuthJWT:
    async def test_create_and_verify_access_token(self):
        tid = 123_456
        token = create_access_token({"sub": str(tid)}, role="admin")

        payload = verify_access_token(token)
        assert payload["sub"] == str(tid)
        assert payload["scope"] == "admin"

    async def test_verify_invalid_access_token(self):
        with pytest.raises(ValueError):
            verify_access_token("not.a.valid.jwt")

    async def test_create_and_rotate_refresh_token(self, db):
        # створимо новий refresh, зразу зробимо ротацію
        user_id = "42"
        refresh = await create_refresh_token(user_id)
        new_access, new_refresh = await verify_and_rotate_refresh_token(refresh)

        assert new_refresh != refresh
        p = verify_access_token(new_access)
        assert p["sub"] == user_id

        # старий refresh тепер недійсний
        with pytest.raises(ValueError):
            await verify_and_rotate_refresh_token(refresh)


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_telegram_flow_and_refresh(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        # 1) Telegram-login → отримуємо пару токенів
        tid = 555_666
        init_data = gen_init_data(tid)

        resp = await client.post(
            "/auth/telegram", 
            json={"init_data": init_data},
            headers=headers)
        print("RESP:::", resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body and "refresh_token" in body

        access = body["access_token"]
        refresh = body["refresh_token"]

        # 2) перевіряємо payload access
        claims = verify_access_token(access)
        assert claims["sub"] == str(tid)
        assert claims["scope"] == "user"

        # 3) Refresh → ротація
        r2 = await client.post(
            "/auth/refresh", 
            json={"refresh_token": refresh},
            headers=headers
            )
        assert r2.status_code == 200
        b2 = r2.json()
        assert b2["refresh_token"] != refresh

        # 4) старий refresh тепер invalid
        r3 = await client.post(
            "/auth/refresh",
            json={"refresh_token": refresh},
            headers=headers
            )
        assert r3.status_code == 401

    async def test_telegram_invalid_init_data(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.post(
            "/auth/telegram", 
            json={"init_data": "foo=bar&hash=baz"},
            headers=headers)
        assert resp.status_code in (400, 401)

    async def test_get_current_user_endpoint(self, client, auth_token):
        # auth_token дає лише access, бо фікстура /dev/user/create повертає access
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/users/me", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == 42
        assert "username" in data


@pytest.mark.asyncio
class TestProtectedRoutesWithRole:
    async def test_user_cannot_access_admin(self, client, auth_token):
        # дефолтний auth_token налаштований на user
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/admin/dashboard", headers=headers)
        assert resp.status_code == 403

    # async def test_admin_can_access(self, client, db):
    #     # піднімаємо існуючого user (telegram_id=42) до ролі admin
    #     user = await UserService.get_user_by_telegram_id(42)
    #     user.role = "admin"
    #     await user.save()

    #     token_admin = create_access_token({"sub": str(user.user_id)}, role="admin")
    #     headers = {"Authorization": f"Bearer {token_admin}"}

    #     resp = await client.get("/admin/dashboard", headers=headers)
    #     assert resp.status_code == 200
    #     msg = resp.json().get("msg", "")
    #     assert "admin" in msg.lower()
