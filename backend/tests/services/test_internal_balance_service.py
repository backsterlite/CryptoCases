import pytest

from decimal import Decimal
from unittest.mock import AsyncMock


from src.app.services.internal_balance_service import InternalBalanceService
from src.app.db.models.internal_balance import InternalBalance



@pytest.mark.asyncio
class TestInternalBalanceService:
    async def test_adjust_balance_credit(self, monkeypatch):
        collection = InternalBalance
        monkeypatch.setattr(collection.get_motor_collection(), 'update_one', AsyncMock())
        await InternalBalanceService.adjust_balance(1, 'usdt', None, Decimal('5'))

    async def test_adjust_balance_debit_insufficient(self, monkeypatch):
        res = AsyncMock(matched_count=0)
        monkeypatch.setattr(InternalBalance.get_motor_collection(), 'update_one', AsyncMock(return_value=res))
        with pytest.raises(Exception):
            await InternalBalanceService.adjust_balance(1, 'usdt', None, Decimal('-10'))