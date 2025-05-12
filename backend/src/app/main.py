from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from contextlib import asynccontextmanager

from app.db.init_db import init_db
from app.api.routers import user, balance, rates
from app.exceptions import register_exception_handlers
from app.services.coin_registry import CoinRegistry
from app.services.rate_cache import rate_cache
from app.config.settings import settings

#DEV section
from app.dev import dev_tools
#DEV section



@asynccontextmanager
async def lifespan(app: FastAPI):
    CoinRegistry.load_from_file(path=settings.coin_registry_path)
    asyncio.create_task(rate_cache.rate_updater())
    await init_db()
    yield 
    rate_cache.close()

app = FastAPI(title="CryptoCases API", lifespan=lifespan, debug=True)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],      # або точний URL фронтенду, наприклад "http://localhost:5173"
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(user.router)
app.include_router(balance.router)
app.include_router(rates.router)





#DEV section
app.include_router(dev_tools.router)
#DEV section




@app.get("/")
async def root():
    return {"message": "CryptoCases backend is alive"}

