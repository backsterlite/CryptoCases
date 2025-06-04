from fastapi import APIRouter, Depends

from app.api.deps import require_role
from app.db.models.user import User
from app.services.internal_balance_service import InternalBalanceService

router = APIRouter(prefix="/balance", tags=["Balance"])

@router.get("/usd", response_model=str)
async def get_usd_balance(user: User = Depends(require_role("user"))):
    return await InternalBalanceService.get_overall_balance_by_usd(user.user_id)