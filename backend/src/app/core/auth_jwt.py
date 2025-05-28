import uuid

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import Optional, Dict, Any


from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer


from app.config.settings import settings
from app.services.user_service import UserService
from app.db.models.user import User
from app.core.redis_client import get_redis

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 12 годин
REFRESH_TOKEN_EXPIRE_DAYS = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # формальність, не використовується напряму

def create_access_token(data: Dict[str,Any], role: str) -> str:
    to_encode = data.copy()
    now =  datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "iat": now,
        "scope": role,
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    to_encode = {
        "sub": user_id,
        "jti": jti,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": now,
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Зберігаємо jti в Redis з TTL
    redis = get_redis()
    redis.set(f"refresh_jti:{user_id}", jti, ex=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
    return token


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError("Invalid access token") from e

async def verify_and_rotate_refresh_token(token: str) -> tuple[str, str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if not user_id or not jti:
            raise ValueError("Malformed refresh token")
    except JWTError as e:
        raise ValueError("Invalid refresh token") from e

    redis = get_redis()
    stored_jti = await redis.get(f"refresh_jti:{user_id}")
    if stored_jti != jti:
        raise ValueError("Refresh token revoked")

    # Валідація пройдена — створюємо нову пару
    new_access = create_access_token({"sub": user_id}, role=payload.get("scope", "user"))
    new_refresh = create_refresh_token(user_id)
    return new_access, new_refresh
