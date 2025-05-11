from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config.settings import settings
from app.services.user_service import UserService
from app.db.models.user import User

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # 12 годин

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # формальність, не використовується напряму

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        telegram_id: int = int(payload.get("sub"))
        return telegram_id
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    telegram_id = verify_access_token(token)
    user = await UserService.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
