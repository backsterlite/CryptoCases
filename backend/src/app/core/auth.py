import hmac
import hashlib
import urllib.parse
import json
from typing import Dict, Any

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.user import UserCreateTelegram






def verify_telegram_auth(init_data: str, bot_token: str) -> Dict[str,Any]:
    try:
        parsed = urllib.parse.parse_qs(init_data, keep_blank_values=True)
        parsed = {k: v[0] for k, v in parsed.items()}
        hash_from_telegram = parsed.pop("hash", None)
        
        if not hash_from_telegram:
            raise ValueError("Missing hash")
        
        data_check_string = "\n".join(f"{k}={v}" for k,v in sorted(parsed.items()))
        
        secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
        
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        print(f"calculated_hash: {calculated_hash} | hash_from_telegram : {hash_from_telegram}")
        if calculated_hash != hash_from_telegram:
            raise ValueError("Invalid hash")
        return parsed
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth failed: {str(e)}")
