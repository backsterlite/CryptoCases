from app.main import app as real_app
from app.config.settings_test import TestSettings
from app.db.models.user import User

import pytest_asyncio
import motor.motor_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from beanie import init_beanie




settings = TestSettings()


@pytest_asyncio.fixture(scope="function")
async def test_app() -> FastAPI:
    return real_app

@pytest_asyncio.fixture(scope="function")
async def test_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url)
    db = client[settings.mongo_db_name]
    await init_beanie(database=db, document_models=[User])
    yield db
    await db.drop_collection("users")

@pytest_asyncio.fixture(scope="function")
async def client(test_app: FastAPI, test_db) -> AsyncClient:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac