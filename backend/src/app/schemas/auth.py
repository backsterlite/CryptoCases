from typing import Optional, Dict, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

class LogoutRequest(BaseModel):
    """Схема для логауту"""
    revoke_all: bool = Field(default=False, description="Revoke all refresh tokens")

class TelegramAuthRequestSecure(BaseModel):
    """Розширена схема для Telegram авторизації"""
    init_data: str = Field(..., min_length=1, max_length=4096)
    
    @field_validator('init_data')
    def validate_init_data(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('init_data must be a non-empty string')
        
        # Базова перевірка формату
        if 'hash=' not in v or 'auth_date=' not in v:
            raise ValueError('init_data missing required fields')
        
        return v

class TelegramAuthData(BaseModel):
    """Структура валідних даних з Telegram WebApp"""
    query_id: str
    user: Dict[str, Any]
    auth_date: int
    signature: Optional[str] = None
    hash: Optional[str] = None

class TelegramAuthRequest(BaseModel):
    init_data: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)

class RefreshRequest(BaseModel):
    refresh_token: str
    

class TokenInfo(BaseModel):
    """Інформація про токен"""
    user_id: int
    role: str
    expires_at: str
    token_type: str