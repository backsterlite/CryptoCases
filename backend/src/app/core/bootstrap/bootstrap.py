import asyncio

from app.db.init_db import init_db
from app.config.settings import settings
from app.services.coin_registry import CoinRegistry
from app.services.rate_cache import rate_cache  



async def run():
    CoinRegistry.load_from_file(path=settings.coin_registry_path)
    asyncio.create_task(rate_cache.rate_updater())
    await init_db()
    
def stop():
    rate_cache.close()