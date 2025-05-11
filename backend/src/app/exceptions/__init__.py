from fastapi import FastAPI


def register_exception_handlers(app: FastAPI):
    """
    Register exception handlers for the FastAPI app.
    """
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from app.exceptions.base import AppException
    from app.exceptions.balance import BalanceTooLow
   
    from app.handlers.exception_handlers import (
        app_exception_handler,
        global_exception_handler,
        balance_to_low_exception_handler,
        http_exception_handler,
    )
    
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(BalanceTooLow, balance_to_low_exception_handler)