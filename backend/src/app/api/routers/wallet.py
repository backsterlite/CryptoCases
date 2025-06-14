from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal

from app.schemas.wallet import(
    UserWalletsGrouped,
    ExchangeQuoteRequest,
    ExchangeQuoteResponse,
    ExchangeExecuteRequest,
    ExchangeExecuteResponse
    )
from app.services.exchange_service import ExchangeService
from app.api.deps import require_role
from app.db.models.user import User
from app.utils.user import group_wallets_by_coin
from . import API_V1


router = APIRouter(prefix=f"{API_V1}/wallet", tags=["Wallets"])


@router.get('/all', response_model=UserWalletsGrouped)
async def get_wallets(
    user: User = Depends(require_role("user"))
):
    return await group_wallets_by_coin(user_id=user.user_id)

@router.post('/swap/quote', response_model=ExchangeQuoteResponse)
async def check_swap_quote(
    data: ExchangeQuoteRequest,
    user: User = Depends(require_role("user"))
):
    ExchangeService.validate(data)
    to_amount = await ExchangeService.quote(
        from_token=data.from_token,
        from_network=data.from_network,
        to_token=data.to_token,
        to_network=data.to_network,
        from_amount=data.from_amount
    )
    result = ExchangeQuoteResponse(
        from_token=data.from_token,
        from_network=data.from_network,
        to_token=data.to_token,
        to_network=data.to_network,
        to_amount=to_amount
    )
    return result

@router.post('/swap/execute', response_model=ExchangeExecuteResponse)
async def execute_swap(
    data: ExchangeExecuteRequest,
    user: User = Depends(require_role("user"))
):
    ExchangeService.validate(data)
    result = await ExchangeService.execute(
        user_id=user.user_id,
        from_token=data.from_token,
        from_network=data.from_network,
        to_token=data.to_token,
        to_network=data.to_network,
        from_amount=data.from_amount
    )
    return ExchangeExecuteResponse(from_amount=result[0], to_amount=result[1])