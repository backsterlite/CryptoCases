import asyncio
import logging
import json

from typing import List, Dict, Optional
from aiocache import caches, Cache
from aiohttp import ClientSession, ClientError, ClientTimeout
from decimal import Decimal
from pathlib import Path

from app.core.config.coin_registry import CoinRegistry
from app.core.config.settings import Settings, BASE_DIR
from app.core.config.settings import get_settings



logger = logging.getLogger(__name__)
caches.set_config({"default": {"cache": "aiocache.SimpleMemoryCache"}})

def chunk_list(lst: List[str], size: int) -> List[List[str]]:
    """Розбиває список на чанки заданого розміру."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]

class RateCache:
    def __init__(
        self,
        batch_size: int = 50,
        timeout_seconds: int = 5,
    ):
        self.batch_size = batch_size
        # пункт 1 & 3: створюємо одну сесію з таймаутом
        self._timeout = ClientTimeout(total=timeout_seconds)
        self._session: Optional[ClientSession] = None
        self._settings = get_settings()

    async def close(self):
        """Закриваємо сесію при завершенні роботи."""
        await self._session.close() # type: ignore
        
    async def _ensure_session(self):
        if self._session is None:
            self._session = ClientSession(timeout=self._timeout)

    async def _fetch_rates(self) -> Dict[str, Decimal]:
        await self._ensure_session()
        # пункт 1: беремо актуальні id кожного разу
        ids = CoinRegistry.list_ids() or []
        if not ids:
            return {}

        results: Dict[str, Decimal] = {}

        # пункт 5: батчимо запити по batch_size
        for batch in chunk_list(ids, self.batch_size):
            params = {
                "ids": ",".join(batch),      # пункт 2: params замість ручного f-string у URL
                "vs_currencies": "usd"
            }
            try:
                resp = await self._session.get( # type: ignore
                    f"{self._settings.COINGECKO_BASE_URL}/simple/price",
                    params=params
                )
                resp.raise_for_status()      # пункт 3: перевірка статусу
                data = await resp.json()
            except (ClientError, asyncio.TimeoutError) as e:
                logger.error("Error fetching rates for batch %s: %s", batch, e)
                continue

            # пункт 4: ітеруємося по тому, що реально прийшло
            for key, obj in data.items():
                usd_val = obj.get("usd")
                if usd_val is None:
                    logger.warning("No USD price for %s in response", key)
                    continue
                try:
                    results[key] = Decimal(str(usd_val))
                except (ValueError, TypeError) as e:
                    logger.error("Can't parse USD value for %s: %s", key, e)
            await asyncio.sleep(1)
        with open(Path( "/app/data/rate_cache.json"), "w") as f:
            json.dump(results, f, indent=2, default=str, ensure_ascii=False)
        return results

    async def rate_updater(self, interval_seconds: int = 300) -> None:
        """
        Фоновий таск, що кожні interval_seconds оновлює cache["coin_rates"].
        Запускай як: asyncio.create_task(rate_cache.rate_updater())
        """
        cache = caches.get("default")
        while True:
            rates = await self._fetch_rates()
            await cache.set("coin_rates", rates) # type: ignore
            logger.info("Coin rates updated, next in %s sec", interval_seconds)
            await asyncio.sleep(interval_seconds)

    async def get_rate(self, coin_id: str) -> Decimal:
        """
        Повертає курс конкретної монети з кешу (або 0, якщо немає).
        """
        cache = caches.get("default")
        rates: Dict[str, Decimal] = await cache.get("coin_rates", {})  # type: ignore # {} for default
        return rates.get(coin_id, Decimal("0"))
    
    async def get_all_rates(self) -> Dict[str, str]:
        cache = caches.get("default")
        rates = await cache.get("coin_rates", {}) or {} # type: ignore
        return {sym: str(rt) for sym, rt in rates.items()}
    
    
    async def force_update(self):
        cache = caches.get("default")
        rates = await self._fetch_rates()
        await cache.set("coin_rates", rates) # type: ignore

rate_cache = RateCache()