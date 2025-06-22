# backend/src/app/core/middlewares/security_middleware.py
import time
import logging
from typing import Dict, Set, Optional, List
import asyncio
from collections import defaultdict, deque

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware для додаткової безпеки API
    """
    
    def __init__(
        self,
        app,
        max_requests_per_minute: int = 60,
        max_requests_per_hour: int = 1000,
        blocked_ips: Set[str] = set(),
        trusted_proxies: Set[str] = set()
    ):
        super().__init__(app)
        self.max_requests_per_minute = max_requests_per_minute
        self.max_requests_per_hour = max_requests_per_hour
        self.blocked_ips = blocked_ips or set()
        self.trusted_proxies = trusted_proxies or set()
        
        # Rate limiting storage
        self.ip_requests: Dict[str, deque] = defaultdict(deque)
        self.failed_auth_attempts: Dict[str, deque] = defaultdict(deque)
        
        # Suspicious activity detection
        self.suspicious_patterns = {
            '/auth/telegram': 5,  # max 5 attempts per minute
            '/auth/refresh': 10,  # max 10 attempts per minute
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get real client IP
        client_ip = self._get_client_ip(request)
        
        # Security checks
        try:
            await self._check_blocked_ip(client_ip)
            await self._check_rate_limits(client_ip, request.url.path)
            await self._check_request_size(request)
            await self._check_suspicious_headers(request)
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        
        # Process request
        response = await call_next(request)
        
        # Log security events
        await self._log_request(request, response, client_ip, start_time)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Отримання справжнього IP клієнта"""
        
        # Перевіряємо X-Forwarded-For тільки від довірених проксі
        if request.client and request.client.host in self.trusted_proxies:
            forwarded_for = request.headers.get("X-Forwarded-For")
            if forwarded_for:
                # Беремо перший IP (клієнт)
                return forwarded_for.split(",")[0].strip()
        
        # Інші заголовки для отримання IP
        for header in ["X-Real-IP", "X-Client-IP"]:
            ip = request.headers.get(header)
            if ip:
                return ip.strip()
        
        # Fallback до IP з request.client
        return request.client.host if request.client else "unknown"
    
    async def _check_blocked_ip(self, ip: str):
        """Перевірка чи IP не заблокований"""
        if ip in self.blocked_ips:
            logger.warning(f"Blocked IP {ip} attempted access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    async def _check_rate_limits(self, ip: str, path: str):
        """Перевірка rate limiting"""
        current_time = time.time()
        
        # Очищаємо старі записи
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        requests = self.ip_requests[ip]
        
        # Видаляємо запити старші за годину
        while requests and requests[0] < hour_ago:
            requests.popleft()
        
        # Перевірка ліміту за годину
        if len(requests) >= self.max_requests_per_hour:
            logger.warning(f"IP {ip} exceeded hourly rate limit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Перевірка ліміту за хвилину
        recent_requests = [t for t in requests if t > minute_ago]
        if len(recent_requests) >= self.max_requests_per_minute:
            logger.warning(f"IP {ip} exceeded minute rate limit")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Перевірка специфічних endpoint'ів
        if path in self.suspicious_patterns:
            endpoint_limit = self.suspicious_patterns[path]
            endpoint_requests = len([t for t in requests if t > minute_ago])
            if endpoint_requests >= endpoint_limit:
                logger.warning(f"IP {ip} exceeded endpoint rate limit for {path}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Endpoint rate limit exceeded"
                )
        
        # Додаємо поточний запит
        requests.append(current_time)
    
    async def _check_request_size(self, request: Request):
        """Перевірка розміру запиту"""
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                # Ліміт 10MB для всіх запитів
                if size > 10 * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Request too large"
                    )
            except ValueError:
                pass
    
    async def _check_suspicious_headers(self, request: Request):
        """Перевірка підозрілих заголовків"""
        
        # Перевірка User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_agents = [
            "bot", "crawler", "spider", "scraper", 
            "wget", "curl", "python-requests"
        ]
        
        # Дозволяємо деякі легітимні requests
        if any(agent in user_agent for agent in suspicious_agents):
            if not any(legit in user_agent for legit in ["telegram", "postman"]):
                logger.info(f"Suspicious user agent: {user_agent}")
        
        # Перевірка на відсутність важливих заголовків
        if request.url.path.startswith("/api/"):
            if not request.headers.get("accept"):
                logger.warning("Request without Accept header")
    
    async def _log_request(
        self, 
        request: Request, 
        response: Response, 
        client_ip: str, 
        start_time: float
    ):
        """Логування запитів для аудиту"""
        
        duration = time.time() - start_time
        
        # Логуємо помилки автентифікації
        if response.status_code == 401:
            failed_attempts = self.failed_auth_attempts[client_ip]
            failed_attempts.append(time.time())
            
            # Очищаємо старі записи (за останні 15 хвилин)
            cutoff = time.time() - 900
            while failed_attempts and failed_attempts[0] < cutoff:
                failed_attempts.popleft()
            
            # Якщо забагато невдалих спроб
            if len(failed_attempts) > 10:
                logger.warning(
                    f"IP {client_ip} has {len(failed_attempts)} "
                    f"failed auth attempts in 15 minutes"
                )
        
        # Логуємо повільні запити
        if duration > 5.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.2f}s from IP {client_ip}"
            )
        
        # Логуємо помилки сервера
        if response.status_code >= 500:
            logger.error(
                f"Server error: {response.status_code} for "
                f"{request.method} {request.url.path} from IP {client_ip}"
            )
    
    def _add_security_headers(self, response: Response):
        """Додавання заголовків безпеки"""
        
        # Захист від XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy (базовий)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

# Middleware для CORS з додатковою безпекою
class SecureCORSMiddleware(BaseHTTPMiddleware):
    """
    Безпечний CORS middleware
    """
    
    def __init__(
        self,
        app,
        allowed_origins: Optional[List[str]] = None,
        allow_credentials: bool = True,
        max_age: int = 86400
    ):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
        self.allow_credentials = allow_credentials
        self.max_age = max_age
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Перевірка origin
        if origin and origin not in self.allowed_origins:
            logger.warning(f"Blocked CORS request from origin: {origin}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Origin not allowed"}
            )
        
        response = await call_next(request)
        
        # Додаємо CORS заголовки тільки для дозволених origins
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = str(self.allow_credentials).lower()
            response.headers["Access-Control-Max-Age"] = str(self.max_age)
            
            if request.method == "OPTIONS":
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
                response.headers["Access-Control-Allow-Headers"] = (
                    "Accept, Accept-Language, Content-Language, Content-Type, Authorization"
                )
        
        return response