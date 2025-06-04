# src/app/api/history.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.history import (
    SpinHistoryResponse, SpinHistoryItem,
    DepositHistoryResponse, DepositHistoryItem,
    WithdrawalHistoryResponse, WithdrawalHistoryItem,
)
from app.services.history_service import HistoryService
from app.api.deps import require_role


router = APIRouter(prefix="/history", tags=["history"])


@router.get(
    "/spins",
    response_model=SpinHistoryResponse,
    summary="Spin history for the current user",
)
async def get_spin_history(
    current_user=Depends(require_role("user")),
    limit: int = 20,
    offset: int = 0
):
    """
    Returns the last `limit` spin records for the current user, sorted by time in descending order.
    """
    user_id = current_user.id
    items = await HistoryService.get_spins(user_id=user_id, limit=limit)
    return SpinHistoryResponse(spins=items)


@router.get(
    "/deposits",
    response_model=DepositHistoryResponse,
    summary="Deposit history for the current user",
)
async def get_deposit_history(
    current_user=Depends(require_role("user")),
    limit: int = 20,
    offset: int = 0
):
    """
    Returns the last `limit` deposit records for the current user, sorted by time in descending order.
    """
    user_id = current_user.id
    items = await HistoryService.get_deposits(user_id=user_id, limit=limit)
    return DepositHistoryResponse(deposits=items)


@router.get(
    "/withdrawals",
    response_model=WithdrawalHistoryResponse,
    summary="Withdrawal history for the current user",
)
async def get_withdrawal_history(
    current_user=Depends(require_role("user")),
    limit: int = 20,
    offset: int = 0
):
    """
    Returns the last `limit` withdrawal records for the current user, sorted by time in descending order.
    """
    user_id = current_user.id
    items = await HistoryService.get_withdrawals(user_id=user_id, limit=limit)
    return WithdrawalHistoryResponse(withdrawals=items)
