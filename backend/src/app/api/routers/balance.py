from fastapi import APIRouter, Depends

from app.core.auth_jwt import get_current_user
from app.db.models.user import User
from app.services.balance_service import BalanceService

router = APIRouter(prefix="/balance", tags=["Balance"])

@router.get("/usd", response_model=str)
async def get_usd_balance(user: User = Depends(get_current_user)):
    return await BalanceService.get_overall_balance_by_usd(user.telegram_id)