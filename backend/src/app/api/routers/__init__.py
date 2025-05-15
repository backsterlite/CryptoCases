from fastapi import FastAPI
from typing import NoReturn


def register_routers(app: FastAPI) -> NoReturn:
    """
    Register all router for the app
    """
    from app.api.routers.user import router as user_router
    from app.api.routers.auth import router as auth_router
    from app.api.routers.balance import router as balance_router
    from app.api.routers.case import router as case_router
    from app.api.routers.fairness import router as fairness_router
    from app.api.routers.rates import router as rate_router
    from app.api.routers.wallet import router as wallet_router
    
    app.include_router(user_router)
    app.include_router(auth_router)
    app.include_router(balance_router)
    app.include_router(case_router)
    app.include_router(fairness_router)
    app.include_router(rate_router)
    app.include_router(wallet_router)