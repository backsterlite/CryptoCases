import hashlib
import pytest
from httpx import AsyncClient
from beanie import PydanticObjectId
from app.db.models.player import ServerSeed, SpinLog
from app.services.fairness_service import FairnessService

@pytest.mark.anyio
class TestFairnessEndpoints:

    async def test_commit_and_reveal(self, client: AsyncClient, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/openapi.json")
        # 1) Commit
        resp = await client.post("/fairness/commit", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        sid = data["server_seed_id"]
        hash0 = data["hash"]
        # в БД seed зберігся й unused
        ss = await ServerSeed.get(PydanticObjectId(sid))
        assert ss and not ss.used
        assert ss.hash == hash0

        # 2) Simulate spin to get spin_log_id
        body = {
            "case_id": "case_5",
            "client_seed": "foo",
            "nonce": 1,
            "server_seed_id": sid
        }
        resp2 = await client.post("/cases/open", json=body, headers=headers)
        print("RESPONSE TRACE", resp2.status_code, resp.json())
        assert resp2.status_code == 200
        spin = resp2.json()
        log_id = spin["spin_log_id"]

        # 3) Reveal
        resp3 = await client.get(f"/fairness/reveal/{log_id}", headers=headers)
        assert resp3.status_code == 200
        rev = resp3.json()
        # перевірка цілісності
        h1 = hashlib.sha256(bytes.fromhex(rev["server_seed"])).hexdigest()
        assert h1 == hash0
        assert rev["table_id"] == spin["table_id"]
        assert rev["odds_version"] == spin["odds_version"]

    async def test_reveal_invalid_log(self, client: AsyncClient, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        # несправжній ID
        resp = await client.get("/fairness/reveal/000000000000000000000000", headers=headers)
        assert resp.status_code == 404
