from fastapi import APIRouter, Depends

from app.schemas.user import  UserResponsePublic
from app.api.deps import get_current_user
from app.db.models.user import User
from app.utils.user import group_wallets_by_coin
from app.schemas.user_wallets import UserWalletsGrouped


router = APIRouter(prefix="/users", tags=["Users"])





# @router.post("/", response_model=UserResponsePublic)
# async def create_user(user: UserCreate):
#     user = await UserService.get_or_create_user(user.telegram_id)
#     return user


@router.get("/me", response_model=UserResponsePublic)
async def get_user(user: User = Depends(get_current_user)):
    return UserResponsePublic(
        user_id=user.user_id,
        username=user.user_name
        
    )

@router.get("/me/wallets", response_model=UserWalletsGrouped)
async def get_balance(user: User = Depends(get_current_user)):
    """
    Get the balance of the current user.
    """
    return UserWalletsGrouped(group_wallets_by_coin(user.wallets))
    