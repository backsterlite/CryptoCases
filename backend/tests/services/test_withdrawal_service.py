import pytest

from decimal import Decimal
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status


from src.app.services.withdrawal_service import WithdrawalService
from src.app.db.models.withdrawal_log import WithdrawalLog


@pytest.mark.asyncio
class TestWithdrawalService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.registry = AsyncMock()
        self.svc = WithdrawalService(registry=self.registry)

    async def test_deduct_internal_balance_insufficient(self):
        with patch('app.services.withdrawal_service.InternalBalanceService.deduct_usd_amount', AsyncMock(side_effect=ValueError('no funds'))):
            with pytest.raises(HTTPException) as exc:
                await self.svc.deduct_internal_balance(1, Decimal('100'))
            assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_withdrawal_log(self):
        log = await self.svc.create_withdrawal_log(10, 'w1', '0xA', Decimal('5'), 'pending', 'eth')
        assert isinstance(log, WithdrawalLog)
        assert log.user_id == 10
        assert log.to_address == '0xA'
        assert log.status == 'pending'

    async def test_execute_transaction_error(self, monkeypatch):
        log = WithdrawalLog(
            user_id=1,
            external_wallet_id='w',
            network='eth',
            to_address='0xB',
            amount_coin=Decimal('1'),
            amount_usdt=Decimal('1'),
            conversion_rate=Decimal('1'),
            status='pending'
            )
        monkeypatch.setattr('app.services.withdrawal_service.BlockchainClientFactory', AsyncMock(side_effect=Exception('fail')))
        with pytest.raises(HTTPException):
            await self.svc.execute_transaction(log, '0xC', 18)