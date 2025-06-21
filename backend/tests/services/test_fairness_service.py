import pytest
import hashlib


from fastapi import HTTPException
from unittest.mock import AsyncMock
from beanie import PydanticObjectId


from src.app.services.fairness_service import FairnessService
from src.app.db.models.player import ServerSeed


@pytest.mark.asyncio
class TestFairnessService:
    async def test_reveal_and_verify_success(self, monkeypatch):
        fake_raw = {'_id': 'id', 'owner_id': '42', 'used': False, 'seed': 'aabb', 'hash': hashlib.sha256(bytes.fromhex('aabb')).hexdigest()}
        monkeypatch.setattr(ServerSeed.get_motor_collection(), 'find_one_and_update', AsyncMock(return_value=fake_raw))
        seed = await FairnessService.reveal_and_verify(PydanticObjectId('id'), 42)
        assert seed.used

    async def test_reveal_and_verify_invalid(self, monkeypatch):
        monkeypatch.setattr(ServerSeed.get_motor_collection(), 'find_one_and_update', AsyncMock(return_value=None))
        with pytest.raises(HTTPException) as exc:
            await FairnessService.reveal_and_verify(PydanticObjectId('bad'), 1)
        assert exc.value.status_code == 400