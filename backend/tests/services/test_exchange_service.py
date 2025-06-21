import pytest

from decimal import Decimal
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch


from src.app.services.exchange_service import ExchangeService

class DummyRateCache:
    async def get_rate(self, coin_id):
        return Decimal('2') if coin_id == 'btc' else Decimal('0')

@pytest.mark.asyncio
class TestExchangeService:
    async def test_validate_unsupported_token(self):
        with patch('app.services.exchange_service.CoinRegistry.get', return_value=None):
            with pytest.raises(HTTPException):
                ExchangeService._validate_token_exists('foo')

    async def test_validate_same_tokens(self):
        data = AsyncMock(from_token='USDT', from_network=None, to_token='USDT', to_network=None)
        with pytest.raises(HTTPException):
            ExchangeService._validate_different_tokens('USDT', None, 'USDT', None)