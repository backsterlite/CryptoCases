from typing import Optional
from fastapi import APIRouter, Depends

from app.schemas.admin.history.deposit import DepositHistoryListResponse
from app.schemas.admin.history.spin import SpinLogListResponse
from app.schemas.admin.history.withdrawal import WithdrawalHistoryListResponse
from app.services.history_service import HistoryService
from app.api.deps import require_role
from .. import API_V1
router = APIRouter(prefix=f"{API_V1}/admin/history", tags=["admin"])


@router.get("/spins", response_model=SpinLogListResponse)
async def get_spin_history_admin(
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    current_admin=Depends(require_role("admin")),
):
    items = await HistoryService.get_spins_admin(limit=limit, offset=offset, user_id=user_id)
    return SpinLogListResponse(spins=items)


@router.get("/deposits", response_model=DepositHistoryListResponse)
async def get_deposit_history_admin(
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    current_admin=Depends(require_role("admin")),
):
    items = await HistoryService.get_deposits_admin(limit=limit, offset=offset, user_id=user_id)
    return DepositHistoryListResponse(deposits=items)


@router.get("/withdrawals", response_model=WithdrawalHistoryListResponse)
async def get_withdrawal_history_admin(
    limit: int = 20,
    offset: int = 0,
    user_id: Optional[str] = None,
    current_admin=Depends(require_role("admin")),
):
    items = await HistoryService.get_withdrawals_admin(limit=limit, offset=offset, user_id=user_id)
    return WithdrawalHistoryListResponse(withdrawals=items)