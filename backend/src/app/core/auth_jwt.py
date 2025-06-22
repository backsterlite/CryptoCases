# backend/src/app/core/auth_jwt.py
import uuid
import secrets
import json
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt, ExpiredSignatureError
from typing import Optional, Dict, Any, Tuple
import logging

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config.settings import get_settings
from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)

class JWTConfig:
    """Конфігурація JWT токенів"""
    
    def __init__(self):
        self.settings = get_settings()
        self.SECRET_KEY = self._get_secret_key()
        self.ALGORITHM = "HS256"
        
        # Безпечні налаштування часу життя
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 хвилин
        self.REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 днів (замість 30)
        self.REFRESH_TOKEN_ROTATE_THRESHOLD = 24 * 60  # Ротація після 1 дня
        
        # Максимальна кількість активних refresh токенів на користувача
        self.MAX_REFRESH_TOKENS_PER_USER = 5
    
    def _get_secret_key(self) -> str:
        """Отримання та валідація JWT секретного ключа"""
        secret = self.settings.jwt_secret
        
        if not secret:
            raise ValueError("JWT_SECRET is required")
        
        if len(secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        
        return secret

# Глобальний екземпляр конфігурації
jwt_config = JWTConfig()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/telegram")

class JWTManager:
    """Менеджер для роботи з JWT токенами"""
    
    @staticmethod
    def create_access_token(
        user_id: int, 
        role: str = "user",
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Створення access токена з додатковими мірами безпеки"""
        
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user_id")
        
        if role not in jwt_config.settings.ROLE_PRIORITIES:
            raise ValueError(f"Invalid role: {role}")
        
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Базові claims
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": now,
            "nbf": now,  # Not Before - токен не дійсний до цього часу
            "iss": "cryptocases-api",  # Issuer
            "aud": "cryptocases-client",  # Audience
            "scope": role,
            "jti": str(uuid.uuid4()),  # Унікальний ID токена
            "token_type": "access"
        }
        
        # Додаткові claims
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            token = jwt.encode(
                payload, 
                jwt_config.SECRET_KEY, 
                algorithm=jwt_config.ALGORITHM
            )
            logger.info(f"Created access token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed"
            )
    
    @staticmethod
    async def create_refresh_token(user_id: int) -> str:
        """Створення refresh токена з ротацією"""
        
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("Invalid user_id")
        
        redis = get_redis()
        user_key = f"refresh_tokens:{user_id}"
        
        try:
            # Перевіряємо кількість активних токенів
            active_tokens = await redis.llen(user_key)
            if active_tokens >= jwt_config.MAX_REFRESH_TOKENS_PER_USER:
                # Видаляємо найстаріший токен
                await redis.lpop(user_key)
            
            now = datetime.now(timezone.utc)
            expire = now + timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS)
            
            # Генеруємо унікальний JTI
            jti = secrets.token_urlsafe(32)
            
            payload = {
                "sub": str(user_id),
                "exp": expire,
                "iat": now,
                "nbf": now,
                "iss": "cryptocases-api",
                "aud": "cryptocases-client",
                "jti": jti,
                "token_type": "refresh"
            }
            
            token = jwt.encode(
                payload,
                jwt_config.SECRET_KEY,
                algorithm=jwt_config.ALGORITHM
            )
            
            # Зберігаємо JTI в Redis з TTL
            token_data = {
                "jti": jti,
                "created_at": now.isoformat(),
                "last_used": now.isoformat()
            }
            
            await redis.rpush(user_key, jti)
            await redis.expire(user_key, jwt_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600)
            await redis.setex(
                f"refresh_jti:{jti}",
                jwt_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                json.dumps(token_data)
            )
            
            logger.info(f"Created refresh token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Failed to create refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Token generation failed"
            )
    
    @staticmethod
    def verify_access_token(token: str) -> Dict[str, Any]:
        """Валідація access токена"""
        try:
            payload = jwt.decode(
                token,
                jwt_config.SECRET_KEY,
                algorithms=[jwt_config.ALGORITHM],
                audience="cryptocases-client",
                issuer="cryptocases-api"
            )
            
            # Додаткові перевірки
            if payload.get("token_type") != "access":
                raise ValueError("Invalid token type")
            
            # Перевірка user_id
            user_id = payload.get("sub")
            if not user_id or not user_id.isdigit():
                raise ValueError("Invalid user_id in token")
            
            return payload
            
        except ExpiredSignatureError:
            raise ValueError("Token expired")
        except JWTError as e:
            raise ValueError(f"Invalid token: {e}")
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Token validation failed")
    
    @staticmethod
    async def verify_and_rotate_refresh_token(token: str) -> Tuple[str, str]:
        """Валідація та ротація refresh токена"""
        try:
            # Декодуємо токен
            payload = jwt.decode(
                token,
                jwt_config.SECRET_KEY,
                algorithms=[jwt_config.ALGORITHM],
                audience="cryptocases-client",
                issuer="cryptocases-api"
            )
            
            user_id = payload.get("sub")
            jti = payload.get("jti")
            token_type = payload.get("token_type")
            
            if not user_id or not jti or token_type != "refresh":
                raise ValueError("Invalid refresh token structure")
            
            redis = get_redis()
            
            # Перевіряємо чи токен не був відкликаний
            token_data = await redis.get(f"refresh_jti:{jti}")
            if not token_data:
                raise ValueError("Refresh token revoked or expired")
            
            # Оновлюємо час останнього використання
            token_info = json.loads(token_data)
            token_info["last_used"] = datetime.now(timezone.utc).isoformat()
            await redis.setex(
                f"refresh_jti:{jti}",
                jwt_config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
                json.dumps(token_info)
            )
            
            # Отримуємо роль користувача з бази даних
            from app.services.user_service import UserService
            user = await UserService.get_user_by_telegram_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            # Створюємо нові токени
            new_access = JWTManager.create_access_token(user.user_id, user.role)
            
            # Створюємо новий refresh токен тільки якщо поточний старий
            iat = datetime.fromtimestamp(payload.get("iat", 0), tz=timezone.utc)
            token_age = datetime.now(timezone.utc) - iat
            
            if token_age.total_seconds() > jwt_config.REFRESH_TOKEN_ROTATE_THRESHOLD * 60:
                # Відкликаємо старий токен
                await redis.delete(f"refresh_jti:{jti}")
                await redis.lrem(f"refresh_tokens:{user_id}", 1, jti)
                
                # Створюємо новий
                new_refresh = await JWTManager.create_refresh_token(user.user_id)
            else:
                new_refresh = token
            
            logger.info(f"Refreshed tokens for user {user_id}")
            return new_access, new_refresh
            
        except ExpiredSignatureError:
            raise ValueError("Refresh token expired")
        except JWTError as e:
            raise ValueError(f"Invalid refresh token: {e}")
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise ValueError("Token refresh failed")
    
    @staticmethod
    async def revoke_refresh_token(jti: str, user_id: int) -> bool:
        """Відкликання конкретного refresh токена"""
        try:
            redis = get_redis()
            
            # Видаляємо токен з Redis
            await redis.delete(f"refresh_jti:{jti}")
            await redis.lrem(f"refresh_tokens:{user_id}", 1, jti)
            
            logger.info(f"Revoked refresh token {jti} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False
    
    @staticmethod
    async def revoke_all_refresh_tokens(user_id: int) -> bool:
        """Відкликання всіх refresh токенів користувача"""
        try:
            redis = get_redis()
            user_key = f"refresh_tokens:{user_id}"
            
            # Отримуємо всі JTI
            jtis = await redis.lrange(user_key, 0, -1)
            
            # Видаляємо всі токени
            for jti in jtis:
                await redis.delete(f"refresh_jti:{jti}")
            
            # Очищаємо список
            await redis.delete(user_key)
            
            logger.info(f"Revoked all refresh tokens for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke all tokens: {e}")
            return False

# Функції для зворотної сумісності
create_access_token = JWTManager.create_access_token
create_refresh_token = JWTManager.create_refresh_token
verify_access_token = JWTManager.verify_access_token
verify_and_rotate_refresh_token = JWTManager.verify_and_rotate_refresh_token