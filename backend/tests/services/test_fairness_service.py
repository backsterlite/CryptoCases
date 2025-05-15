import pytest
import hashlib
from beanie import PydanticObjectId
from fastapi import HTTPException
from app.services.fairness_service import FairnessService
from app.db.models.player import ServerSeed

@pytest.mark.anyio
class TestRevealAndVerify:

    async def test_success_and_mark_used(self, db):
        raw = bytes.fromhex("ff"*32)
        hex_seed = raw.hex()
        hash0 = hashlib.sha256(raw).hexdigest()
        # підкладемо clean seed
        ss = ServerSeed(
            seed=hex_seed,
            hash=hash0,
            owner_id="42"
        )
        await ss.insert()
        # 1-й раз — ок
        doc = await FairnessService.reveal_and_verify(commit_id=ss.id, user_id="42")
        assert doc.used is True
        # 2-й раз — помилка
        with pytest.raises(HTTPException) as ei:
            await FairnessService.reveal_and_verify(commit_id=ss.id, user_id="42")
        assert ei.value.status_code == 400
