# backend/src/app/core/auth.py
import hmac
import hashlib
import urllib.parse
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from fastapi import HTTPException, status
import logging

from app.schemas.auth import TelegramAuthData

logger = logging.getLogger(__name__)


class TelegramAuthValidator:
    """Валідатор для Telegram WebApp init_data"""
    
    # Максимальний вік init_data (5 хвилин)
    MAX_AUTH_AGE_SECONDS = 300
    
    # Обов'язкові поля
    REQUIRED_FIELDS = {"query_id", "user", "auth_date", "hash"}
    
    @classmethod
    def verify_telegram_auth(cls, init_data: str, bot_token: str) -> TelegramAuthData:
        """
        Повна валідація Telegram WebApp init_data згідно з офіційною документацією
        https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
        """
        try:
            # 1. Парсинг URL-encoded даних
            parsed = cls._parse_init_data(init_data)
            
            # 2. Валідація структури
            cls._validate_structure(parsed)
            
            # 3. Валідація часу
            # cls._validate_timestamp(parsed)
            
            # 4. Валідація підпису
            cls._validate_signature(parsed, bot_token)
            
            # 5. Валідація даних користувача
            user_data = cls._validate_user_data(parsed)
            
            return TelegramAuthData(
                query_id=parsed["query_id"],
                user=user_data,
                auth_date=int(parsed["auth_date"]),
                signature=parsed.get("signature"),
                hash=parsed["hash"]
            )
            
        except ValueError as e:
            logger.warning(f"Telegram auth validation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram authentication data"
            )
        except Exception as e:
            logger.error(f"Telegram auth error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service error"
            )
    
    @classmethod
    def _parse_init_data(cls, init_data: str) -> Dict[str, str]:
        """Парсинг URL-encoded init_data"""
        if not init_data or not isinstance(init_data, str):
            raise ValueError("Empty or invalid init_data")
        
        try:
            parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
            # Конвертуємо список значень у одиночні значення
            return {k: v[0] if v else "" for k, v in parsed.items()}
        except Exception as e:
            raise ValueError(f"Failed to parse init_data: {e}")
    
    @classmethod
    def _validate_structure(cls, parsed: Dict[str, str]) -> None:
        """Валідація наявності обов'язкових полів"""
        missing_fields = cls.REQUIRED_FIELDS - set(parsed.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        # Перевірка на порожні значення
        for field in cls.REQUIRED_FIELDS:
            if not parsed.get(field):
                raise ValueError(f"Empty required field: {field}")
    
    @classmethod
    def _validate_timestamp(cls, parsed: Dict[str, str]) -> None:
        """Валідація часової мітки"""
        try:
            auth_date = int(parsed["auth_date"])
        except (ValueError, TypeError):
            raise ValueError("Invalid auth_date format")
        
        current_time = int(time.time())
        age = current_time - auth_date
        
        # Перевірка на майбутній час (допуск 60 секунд на розсинхронізацію)
        if age < -60:
            raise ValueError("auth_date is in the future")
        
        # Перевірка на застарілі дані
        if age > cls.MAX_AUTH_AGE_SECONDS:
            raise ValueError(f"auth_data is too old (age: {age}s, max: {cls.MAX_AUTH_AGE_SECONDS}s)")
    
    @classmethod
    def _validate_signature(cls, parsed: Dict[str, str], bot_token: str) -> None:
        """Валідація HMAC підпису згідно з Telegram WebApp документацією"""
        if not bot_token:
            raise ValueError("Bot token is required")
        local_data = parsed.copy()
        hash_from_telegram = local_data.pop("hash")  # Видаляємо hash для підрахунку
        
        try:
            # 1. Створюємо data_check_string (сортовані параметри)
            data_check_string = "\n".join(
                f"{key}={value}" for key, value in sorted(local_data.items())
            )
            
            # 2. Створюємо секретний ключ згідно з документацією Telegram
            secret_key = hmac.new(
                key=b"WebAppData",
                msg=bot_token.encode("utf-8"),
                digestmod=hashlib.sha256
            ).digest()
            
            # 3. Обчислюємо HMAC
            calculated_hash = hmac.new(
                key=secret_key,
                msg=data_check_string.encode("utf-8"),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # 4. Порівнюємо хеші (захист від timing attacks)
            if not hmac.compare_digest(calculated_hash, hash_from_telegram):
                logger.warning(
                    f"Hash mismatch. Expected: {calculated_hash}, "
                    f"Got: {hash_from_telegram}, "
                    f"Data: {data_check_string[:100]}..."
                )
                raise ValueError("Invalid signature")
                
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Signature validation failed: {e}")
    
    @classmethod
    def _validate_user_data(cls, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Валідація та парсинг даних користувача"""
        user_json = parsed.get("user")
        if not user_json:
            raise ValueError("Missing user data")
        
        try:
            user_data = json.loads(user_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid user JSON: {e}")
        
        # Валідація обов'язкових полів користувача
        required_user_fields = {"id", "first_name"}
        missing_user_fields = required_user_fields - set(user_data.keys())
        if missing_user_fields:
            raise ValueError(f"Missing user fields: {missing_user_fields}")
        
        # Валідація типів
        if not isinstance(user_data.get("id"), int):
            raise ValueError("User ID must be integer")
        
        if user_data["id"] <= 0:
            raise ValueError("Invalid user ID")
        
        # Обмеження довжини рядків (захист від DoS)
        string_limits = {
            "first_name": 64,
            "last_name": 64,
            "username": 32,
            "language_code": 10
        }
        
        for field, max_length in string_limits.items():
            value = user_data.get(field)
            if value and len(str(value)) > max_length:
                raise ValueError(f"Field {field} too long")
        
        return user_data


# Функція для зворотної сумісності
def verify_telegram_auth(init_data: str, bot_token: str) -> Dict[str, Any]:
    """Обгортка для зворотної сумісності"""
    auth_data = TelegramAuthValidator.verify_telegram_auth(init_data, bot_token)
    
    # Повертаємо у старому форматі для compatibility
    return {
        "query_id": auth_data.query_id,
        "user": json.dumps(auth_data.user),
        "auth_date": str(auth_data.auth_date),
        "hash": auth_data.hash
    }