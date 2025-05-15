# tests/conftest.py
import os
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.main import app
from app.config.settings_test import settings as test_settings
from app.db.models.player import ServerSeed, SpinLog, PlayerStat, CapPool
from app.db.models.case_config import CaseConfig
from app.db.models.user import User
from app.db.models.withdrawal import WithdrawalLog

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    return asyncio.get_event_loop()

@pytest.fixture(scope="session")
async def db():
    client = AsyncIOMotorClient(test_settings.mongo_url)
    db = client[test_settings.mongo_db_name]
    await init_beanie(
        database=db,
        document_models=[
            User, ServerSeed, SpinLog, PlayerStat,
            CapPool, CaseConfig, WithdrawalLog
        ]
    )
    yield db
    await client.drop_database(test_settings.mongo_db_name)
    client.close()

@pytest.fixture
async def client(db) -> AsyncClient:
    await CapPool.get_motor_collection().find_one_and_delete(CapPool.id == "main")
    # забезпечуємо, що CapPool є
    await CapPool(id="main", balance=1000.0, sigma_buffer=100.0, max_payout=500.0).insert()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client):
    # створимо тестового юзера через /dev/gen_token
    resp = await client.get("/dev/gen_token", params={
        "telegram_id": 42,
        "bot_token": test_settings.dev_bot_token
    })
    return resp.json()["access_token"]
