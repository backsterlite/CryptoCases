# tests/test_history_api.py

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from httpx import AsyncClient

from src.app.db.models.player import SpinLog # type: ignore
from src.app.db.models.deposit_log import DepositLog # type: ignore
from src.app.db.models.withdrawal_log import WithdrawalLog # type: ignore


@pytest.mark.asyncio
class TestHistoryAPI:
    async def test_get_spin_history_empty(self, client: AsyncClient, auth_token: str):
        """
        Якщо у користувача немає жодних записів SpinLog, 
        endpoint /history/spins повинен повернути { "spins": [] }.
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = await client.get("/history/spins?limit=10", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "spins" in data
        assert isinstance(data["spins"], list)
        assert data["spins"] == []

    async def test_get_spin_history_with_data(self, client: AsyncClient, auth_token: str):
        """
        Створюємо 3 SpinLog для поточного користувача (user_id="42"), 
        очікуємо, що /history/spins?limit=2 поверне два останні записи за created_at DESC.
        """
        # user_id із токена = "42"
        user_id = "42"
        now = datetime.utcnow()

        # Три спіни з різними created_at (так, щоб можна було сортувати)
        spin1 = SpinLog(
            user_id=user_id,
            case_id="case_A",
            server_seed_id="seed1",
            server_seed_hash="hash1",
            server_seed_seed="seed_val1",
            client_seed="client1",
            nonce=1,
            hmac_value=b"",
            raw_roll=Decimal("0.15"),
            table_id="table1",
            odds_version="v1",
            case_tier="tier1",
            prize_id="prize1",
            stake=Decimal("2.5"),
            payout=Decimal("5.0"),
            payout_usd=Decimal("5.0"),
            pity_before=Decimal("0"),
            pity_after=Decimal("0"),
            rtp_session=Decimal("0.95"),
            created_at=now - timedelta(seconds=30),
        )
        await spin1.insert()

        spin2 = SpinLog(
            user_id=user_id,
            case_id="case_B",
            server_seed_id="seed2",
            server_seed_hash="hash2",
            server_seed_seed="seed_val2",
            client_seed="client2",
            nonce=2,
            hmac_value=b"",
            raw_roll=Decimal("0.45"),
            table_id="table2",
            odds_version="v1",
            case_tier="tier2",
            prize_id=None,
            stake=Decimal("3.0"),
            payout=Decimal("0.0"),
            payout_usd=Decimal("0.0"),
            pity_before=Decimal("0"),
            pity_after=Decimal("0"),
            rtp_session=Decimal("0.90"),
            created_at=now - timedelta(seconds=20),
        )
        await spin2.insert()

        spin3 = SpinLog(
            user_id=user_id,
            case_id="case_C",
            server_seed_id="seed3",
            server_seed_hash="hash3",
            server_seed_seed="seed_val3",
            client_seed="client3",
            nonce=3,
            hmac_value=b"",
            raw_roll=Decimal("0.75"),
            table_id="table3",
            odds_version="v2",
            case_tier="tier1",
            prize_id="prize2",
            stake=Decimal("5.0"),
            payout=Decimal("10.0"),
            payout_usd=Decimal("10.0"),
            pity_before=Decimal("0"),
            pity_after=Decimal("0"),
            rtp_session=Decimal("0.97"),
            created_at=now - timedelta(seconds=10),
        )
        await spin3.insert()

        headers = {"Authorization": f"Bearer {auth_token}"}
        # limit=2 → маємо отримати тільки spin3 та spin2 (найновіші)
        response = await client.get("/history/spins?limit=2", headers=headers)
        assert response.status_code == 200

        data = response.json()
        spins = data.get("spins", [])
        assert len(spins) == 2

        # Перевіряємо, що перший елемент — найновіший (case_C), другий — наступний (case_B)
        assert spins[0]["case_id"] == "case_C"
        assert spins[1]["case_id"] == "case_B"
        # Перевіряємо основні поля, які ми маємо повернути
        for idx, expected_case in enumerate(["case_C", "case_B"]):
            item = spins[idx]
            assert "id" in item and isinstance(item["id"], str)
            assert item["case_id"] == expected_case
            # перевіримо, що поля stake/payout/parsing працюють
            assert "stake" in item and "payout" in item


    async def test_get_deposit_history_empty(self, client: AsyncClient, auth_token: str):
        """
        Якщо у користувача немає жодних DepositLog,  
        endpoint /history/deposits повертає { "deposits": [] }.
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/history/deposits?limit=5", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "deposits" in data
        assert data["deposits"] == []

    async def test_get_deposit_history_with_data(self, client: AsyncClient, auth_token: str):
        """
        Створюємо дві транзакції DepositLog для user_id="42", 
        очікуємо, що /history/deposits?limit=1 поверне останній запис.
        """
        user_id = "42"
        now = datetime.utcnow()

        # Перший депозит (старіший)
        dep1 = DepositLog(
            user_id=user_id,
            external_wallet_id="ext_wallet_1",
            tx_hash="0xabc",
            coin="USDT",
            amount=Decimal("100.00"),
            from_address="0xfrom1",
            block_number=12345,
            timestamp=now - timedelta(hours=1),
            confirmations=5,
            status="confirmed",
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        )
        await dep1.insert()

        # Другий депозит (новіший)
        dep2 = DepositLog(
            user_id=user_id,
            external_wallet_id="ext_wallet_1",
            tx_hash="0xdef",
            coin="USDT",
            amount=Decimal("50.50"),
            from_address="0xfrom2",
            block_number=12346,
            timestamp=now - timedelta(minutes=30),
            confirmations=3,
            status="pending_internal",
            created_at=now - timedelta(minutes=30),
            updated_at=now - timedelta(minutes=30),
        )
        await dep2.insert()

        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/history/deposits?limit=1", headers=headers)
        assert resp.status_code == 200

        data = resp.json()
        deposits = data.get("deposits", [])
        # Ми очікуємо лише один (новіший) запис
        assert len(deposits) == 1
        first = deposits[0]
        assert first["tx_hash"] == "0xdef"
        assert first["status"] == "pending_internal"
        assert first["coin"] == "USDT"
        assert "amount" in first and first["amount"] == "50.50"


    async def test_get_withdrawal_history_empty(self, client: AsyncClient, auth_token: str):
        """
        Якщо у користувача немає жодних WithdrawalLog, 
        endpoint /history/withdrawals повертає { "withdrawals": [] }.
        """
        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/history/withdrawals?limit=3", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "withdrawals" in data
        assert data["withdrawals"] == []

    async def test_get_withdrawal_history_with_data(self, client: AsyncClient, auth_token: str):
        """
        Створюємо один WithdrawalLog для user_id="42", 
        очікуємо, що /history/withdrawals?limit=5 поверне цей запис.
        """
        user_id = "42"
        now = datetime.utcnow()

        wdl = WithdrawalLog(
            user_id=user_id,
            external_wallet_id="ext_wallet_1",
            network="ethereum",
            to_address="0xto_me",
            amount_coin=Decimal("25.00"),
            amount_usdt=Decimal("25.00"),
            conversion_rate=Decimal("1.00"),
            fee_coin=Decimal("0.10"),
            fee_usdt=Decimal("0.10"),
            tx_hash="0xwithdraw1",
            block_number=54321,
            confirmations=2,
            status="broadcasted",
            created_at=now - timedelta(minutes=5),
            updated_at=now - timedelta(minutes=5),
        )
        await wdl.insert()

        headers = {"Authorization": f"Bearer {auth_token}"}
        resp = await client.get("/history/withdrawals?limit=5", headers=headers)
        assert resp.status_code == 200

        data = resp.json()
        withdrawals = data.get("withdrawals", [])
        assert len(withdrawals) == 1

        first = withdrawals[0]
        assert first["to_address"] == "0xto_me"
        assert first["status"] == "broadcasted"
        assert first["fee_coin"] == "0.10"
        assert first["amount_coin"] == "25.00"
        assert first["tx_hash"] == "0xwithdraw1"
        assert first["confirmations"] == 2
