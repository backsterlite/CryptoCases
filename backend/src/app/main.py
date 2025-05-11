from fastapi import FastAPI
import asyncio

from contextlib import asynccontextmanager

from app.db.init_db import init_db
from app.api.routers import user
from app.exceptions import register_exception_handlers
from app.services.coin_registry import CoinRegistry
from app.config.settings import settings

#DEV section
from app.dev import dev_tools
#DEV section



@asynccontextmanager
async def lifespan(app: FastAPI):
    CoinRegistry.load_from_file(path=settings.coin_registry_path)
    await init_db()
    yield 
    

app = FastAPI(title="CryptoCases API", lifespan=lifespan, debug=True)

register_exception_handlers(app)

app.include_router(user.router)




#DEV section
app.include_router(dev_tools.router)
#DEV section




@app.get("/")
async def root():
    return {"message": "CryptoCases backend is alive"}

