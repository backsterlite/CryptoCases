import pytest
from httpx import AsyncClient

from app.services.user_service import UserService
from app.db.models.user import User

@pytest.mark.asyncio
class TestUserEndpoints:

    async def test_create_new_user(self, client: AsyncClient):
        # Arrange
        payload = {"telegram_id": 1111}
        print(type(client))
        # Act
        response = await client.post("/users/", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["telegram_id"] == 1111
        assert data["balance_usd"] == 0.0
        assert data['wallets'] == []

    async def test_return_existing_user(self, client: AsyncClient):
        telegram_id = 2222

        # Arrange — створюємо вручну
        await UserService.create_user(telegram_id)

        # Act — викликаємо endpoint
        response = await client.post("/users/", json={"telegram_id": telegram_id})
        assert response.status_code == 200
        data = response.json()

        # Assert — перевіряємо, що користувач не створився заново
        user_count = await User.find(User.telegram_id == telegram_id).count()
        assert user_count == 1  # 💥 Ключова перевірка

        # І що response відповідає очікуваним полям
        assert data["telegram_id"] == telegram_id
        assert data["balance_usd"] == 0.0
        assert data["wallets"] == []
