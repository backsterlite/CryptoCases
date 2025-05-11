from fastapi import APIRouter, Depends, HTTPException

from app.core.auth_jwt import get_current_user
from app.db.models.user import User
from app.services.balance_service import BalanceService

router = APIRouter(prefix="/balance", tags=["Balance"])



@router.patch("/{amount}")
async def update_balance(amount: float, user: User = Depends(get_current_user)):
    """
    Update the balance of the current user.
    """
    # if amount == 0:
    #     raise HTTPException(status_code=400, detail="Amount cannot be zero")
    
    updated_balance = await BalanceService.update_balance(user.telegram_id, amount)
    
    
    return {"balance": updated_balance}