import pytest
from httpx import AsyncClient
from src.app.services.user_service import UserService
from src.app.db.models.user import User

@pytest.mark.asyncio
class TestUserBalanceEndpoints:

    async def test_increase_balance_valid_amount(self, client: AsyncClient):
        telegram_id = 1001
        await UserService.create_user(telegram_id)

        response = await client.patch(f"/users/{telegram_id}/balance", json={"amount": 10})
        assert response.status_code == 200
        user = await UserService.get_user_by_telegram_id(telegram_id)
        assert user.balance_usd == 10

    async def test_decrease_balance_valid_amount(self, client: AsyncClient):
        telegram_id = 1002
        user = await UserService.create_user(telegram_id)
        user.balance_usd = 10
        await user.save()

        response = await client.patch(f"/users/{telegram_id}/balance", json={"amount": -5})
        assert response.status_code == 200
        user = await UserService.get_user_by_telegram_id(telegram_id)
        assert user.balance_usd == 5

    async def test_decrease_balance_below_zero(self, client: AsyncClient):
        telegram_id = 1003
        user = await UserService.create_user(telegram_id)
        user.balance_usd = 10
        await user.save()

        response = await client.patch(f"/users/{telegram_id}/balance", json={"amount": -20})
        assert response.status_code == 400
        user = await UserService.get_user_by_telegram_id(telegram_id)
        assert user.balance_usd == 10  # unchanged

    async def test_zero_amount_allowed(self, client: AsyncClient):
        telegram_id = 1004
        await UserService.create_user(telegram_id)

        response = await client.patch(f"/users/{telegram_id}/balance", json={"amount": 0})
        assert response.status_code == 200
        user = await UserService.get_user_by_telegram_id(telegram_id)
        assert user.balance_usd == 0
