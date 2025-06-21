# tests/conftest.py
import os
from typing import AsyncGenerator, Any


import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from src.app.main import app
from src.app.core.config.settings_test import settings as test_settings
from src.app.db.models import (
    user,
    player,
    case_config,
    case_log,
    withdrawal_log,
    internal_balance,
    deposit_log,
    external_wallet
)
from src.app.db.mongo_codec import codec_options

@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    """Створюємо окремий event loop для всіх async-тестів з рівнем session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db():
    client = AsyncIOMotorClient(test_settings.test_mongo_url)
    db = client.get_database(test_settings.test_mongo_db_name, codec_options=codec_options)
    await init_beanie(
        database=db,
        document_models=[
        user.User,
        player.CapPool,
        player.PlayerStat,
        player.ServerSeed,
        player.SpinLog,
        case_config.CaseConfig,
        case_log.CaseLog,
        external_wallet.ExternalWallet,
        deposit_log.DepositLog,
        internal_balance.InternalBalance,
        withdrawal_log.WithdrawalLog
        ]
    )
    yield db
    await client.drop_database(test_settings.mongo_db_name)
    client.close()

@pytest.fixture
async def client(db) -> AsyncGenerator[AsyncClient,Any]:
    print("DATABASE:", db)
    await player.CapPool.get_motor_collection().find_one_and_delete({"_id": "main"})
    # забезпечуємо, що CapPool є
    await player.CapPool(id="main", balance=1000.0, sigma_buffer=100.0, max_payout=500.0).insert()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_token(client):
    # створимо тестового юзера через /dev/user/create
    resp = await client.post("/dev/user/create", json={
        "telegram_id": 42,
    })
    return resp.json()["access_token"]
