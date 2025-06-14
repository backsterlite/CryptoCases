from fastapi import APIRouter, Depends

from app.schemas.user import  UserResponsePublic
from app.api.deps import require_role
from app.db.models.user import User
from . import API_V1

router = APIRouter(prefix=f"{API_V1}/users", tags=["Users"])





# @router.post("/", response_model=UserResponsePublic)
# async def create_user(user: UserCreate):
#     user = await UserService.get_or_create_user(user.telegram_id)
#     return user


@router.get("/me", response_model=UserResponsePublic)
async def get_user(user: User = Depends(require_role("user"))):
    return UserResponsePublic(
        user_id=user.user_id,
        username=user.user_name,
        user_firstname=user.first_name,
        user_lastname=user.last_name,
        user_username=user.user_name,
        user_photo_url=user.photo_url
        
    )
    