import pytest

from decimal import Decimal
from fastapi import HTTPException, status
from unittest.mock import AsyncMock

from src.app.services.deposit_service import DepositService
from src.app.services.internal_balance_service import InternalBalanceService
from src.app.db.models.external_wallet import ExternalWallet
from src.app.db.models.deposit_log import DepositLog


@pytest.mark.asyncio
class TestDepositService:
    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        # mock registry token_cfg and network
        self.registry = AsyncMock()
        self.registry.token_cfg.return_value = None
        self.registry.get_network.return_value = None
        # mock ExternalWallet.find_one
        monkeypatch.setattr(ExternalWallet, 'find_one', AsyncMock(return_value=None))
        # create service
        self.svc = DepositService(registry=self.registry, external_wallet_service=AsyncMock())

    async def test_handle_incoming_unknown_network(self):
        self.registry.token_cfg.side_effect = Exception()
        with pytest.raises(HTTPException) as exc:
            await self.svc.handle_incoming('tx1', 'addr', 'USDT', 'badnet', Decimal('1'))
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_handle_incoming_wallet_not_found(self, monkeypatch):
        # registry ok
        monkeypatch.setattr(ExternalWallet, 'find_one', AsyncMock(return_value=None))
        with pytest.raises(HTTPException) as exc:
            await self.svc.handle_incoming('tx2', 'addr', 'USDT', 'mainnet', Decimal('2'))
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_handle_incoming_duplicate(self, monkeypatch):
        fake_wallet = AsyncMock(id='w1', user_id=1, address='addr', network='mainnet')
        monkeypatch.setattr(ExternalWallet, 'find_one', AsyncMock(return_value=fake_wallet))
        existing = DepositLog(
            tx_hash='dup',
            external_wallet_id='w1',
            coin='USDT',
            amount=Decimal('1'),
            user_id=1
            )
        monkeypatch.setattr(DepositLog, 'find_one', AsyncMock(return_value=existing))
        result = await self.svc.handle_incoming('dup', 'addr', 'USDT', 'mainnet', Decimal('1'))
        assert result is existing

    async def test_handle_incoming_success(self, monkeypatch):
        fake_wallet = AsyncMock(id='w2', user_id=2, address='addr2', network='mainnet')
        monkeypatch.setattr(ExternalWallet, 'find_one', AsyncMock(return_value=fake_wallet))
        monkeypatch.setattr(DepositLog, 'find_one', AsyncMock(return_value=None))
        insert_mock = AsyncMock()
        monkeypatch.setattr(DepositLog, 'insert', insert_mock)
        adjust_mock = AsyncMock()
        monkeypatch.setattr(InternalBalanceService, 'adjust_balance', adjust_mock)

        result = await self.svc.handle_incoming('tx3', 'addr2', 'USDT', 'mainnet', Decimal('3'))
        insert_mock.assert_awaited_once()
        adjust_mock.assert_awaited_once_with(2, 'USDT', Decimal('3'))
        assert isinstance(result, DepositLog)
