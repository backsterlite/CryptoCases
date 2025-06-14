import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.base import AppException
from app.exceptions.balance import BalanceTooLow
from app.config.settings import settings

async def app_exception_handler(request: Request, exc: AppException):
    content = {"detail": exc.message, "debug":"on" if settings.debug else "off"}
    if settings.debug:
        content["trace"] = traceback.format_stack()
    return JSONResponse(status_code=exc.status_code, content=content)

async def global_exception_handler(request: Request, exc: Exception):
    content = {"detail": "Internal Server Error", "debug":"on" if settings.debug else "off"}
    if settings.debug:
        content["trace"] = traceback.format_exc()
    return JSONResponse(status_code=500, content=content)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    content = {"detail": exc.detail, "debug":"on" if settings.debug else "off"}
    if settings.debug:
        content["trace"] = traceback.format_exc()
    return JSONResponse(status_code=exc.status_code, content=content)
    
async def balance_to_low_exception_handler(request: Request, exc: BalanceTooLow):
    content = {"detail": exc.message, "debug":"on" if settings.debug else "off"}
    if settings.debug:
        content["trace"] = traceback.format_stack()
    return JSONResponse(
        status_code=exc.status_code,
        content=content
    )