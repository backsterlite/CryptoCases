import asyncio

from decimal import Decimal

from fastapi import Depends

from app.db.init_db import DataBase
from app.db.models.player import CapPool
from app.config.settings import Settings
from app.config.coin_registry import CoinRegistry
from app.config.asset_registry import AssetRegistry
from app.services.rate_cache import rate_cache  
from app.services.case_service import CaseService
from app.api.deps import get_settings



async def run(
    settings: Settings = Depends(get_settings)
):
    CoinRegistry.load_from_file(path=settings.coin_registry_path)
    AssetRegistry.load_from_file(path=settings.asset_registry_path)
    asyncio.create_task(rate_cache.rate_updater())
    await DataBase.init_db()
    await init_cap_pool()
    if not await CaseService.check_cases_init():
        await CaseService.init_cases()
    
async def stop():
    await rate_cache.close()
    
    



async def init_cap_pool():
    if not await CapPool.get("main"):
        cap_pool = CapPool(
            balance=Decimal("2000.00"),
            max_payout=Decimal("250.00"),
            sigma_buffer=Decimal("200.00")
        )
        await cap_pool.insert()