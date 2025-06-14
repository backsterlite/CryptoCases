from fastapi import APIRouter

from app.services.rate_cache import rate_cache
from . import API_V1

router = APIRouter(prefix=f"{API_V1}/rates", tags=["Rates"])

@router.get(path="/", response_model=dict[str,str],
    )
async def list_rates():
    return await rate_cache.get_all_rates()

@router.get("/{symbol}", response_model=str)
async def get_rate(symbol: str):
    return str(await rate_cache.get_rate(symbol))