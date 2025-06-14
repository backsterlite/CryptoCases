from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from app.db.models.user import User
from app.api.deps import require_role
from app.exceptions.balance import BalanceTooLow
from app.schemas.case import CaseOpenRequest, CaseOpenResponse, CaseOut
from app.services.spin_controller import spin
from app.services.case_service import CaseService
from app.services.internal_balance_service import InternalBalanceService
from app.db.models.player import ServerSeed, CapPool
from app.db.models.case_config import CaseConfig
from . import API_V1

router = APIRouter(prefix=f"{API_V1}/cases", tags=["Cases"])


@router.get("/precheck")
async def precheck(case_id: str):
 
    pool = await CapPool.get("main")
    case_config = await CaseConfig.find_one(CaseConfig.case_id==case_id)
    assert pool is not None
    assert case_config is not None
    is_ok = pool.balance >= case_config.global_pool_usd * Decimal.from_float(0.05)
    return {"spin": is_ok, "reason": "reserve_low" if not is_ok else None}
   


@router.post("/open", response_model=CaseOpenResponse)
async def open_case_endpoint(
    data: CaseOpenRequest,
    user: User = Depends(require_role("user"))
    ): 
    if await InternalBalanceService.try_charge_user_for_case(
        user_id=user.user_id,
        case_id=data.case_id):
        
        result = await spin(
            user_id=user.user_id,
            data_for_spin=data
            )
        ca = result.prize.coin_amount
        await InternalBalanceService.adjust_balance(
            user_id=user.user_id,
            coin=ca[0],
            network=ca[1],
            delta=ca[2]
        )
        return result
    else:
        raise BalanceTooLow(None)

@router.get("/list", response_model=List[CaseOut])
async def get_cases_list(
    user: User = Depends(require_role("user"))
):
    return await CaseService.get_all_cases()


@router.get('/get_one', response_model=CaseOut)
async def get_one_case(
    case_id: str,
    user: User = Depends(require_role("user"))
):
    return await CaseService.get_case_by_id(case_id)