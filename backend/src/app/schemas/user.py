import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from app.models.coin import CoinAmount



class UserCreateTelegram(BaseModel):
    telegram_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None

def parse_telegram_init(init_data: Dict[str, Any]) -> UserCreateTelegram:
    # init_data приходить приблизно в такому вигляді:
    # {
    #   'user': ['{"id":123,...}'],
    #   'auth_date': ['1747858930'],
    #   'hash': ['...']
    # }
    
    # 1. Дістаємо JSON-рядок з ключа 'user'
    user_json_list = init_data.get('user')
    if not user_json_list:
        raise ValueError("Missing 'user' in init_data")
    user_obj = json.loads(user_json_list)
    
    # 2. Мапимо поля із Telegram у вашу схему
    user_create = UserCreateTelegram(
        telegram_id=user_obj['id'],
        first_name=user_obj.get('first_name'),
        last_name=user_obj.get('last_name'),
        username=user_obj.get('username'),
        language_code=user_obj.get('language_code')
    )
    return user_create

class UserResponsePublic(BaseModel):
    user_id: int
    username: str | None
    user_firstname: str | None
    user_lastname: str | None
    user_username: str | None
    user_photo_url: str | None

    model_config = ConfigDict( from_attributes=True)
    
class UserResponsePrivate(BaseModel):
    id: Optional[str] = Field(alias="_id")
    user_id: int
    user_firstname: str
    user_lastname: str
    user_username: str
    user_photo_url: str

    model_config = ConfigDict( from_attributes=True)