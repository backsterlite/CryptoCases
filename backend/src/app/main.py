from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.api.routers import register_routers
from app.exceptions import register_exception_handlers
from app.core.bootstrap import bootstrap
from app.config.settings import settings
from app.core import api_limiter


#DEV section
from app.dev import dev_tools
#DEV section



@asynccontextmanager
async def lifespan(app: FastAPI):
    await bootstrap.run()
    yield 
    await bootstrap.stop()

app = FastAPI(title="CryptoCases API", lifespan=lifespan, debug=settings.debug)

# ==== SlowAPI rate‐limiting setup ====
#  створюємо лімітер, ключ за IP

app.state.limiter = api_limiter.limiter
# додаємо middleware, щоб SlowAPI міг ловити запити
app.add_middleware(SlowAPIMiddleware)
# обробник 429 помилок
app.add_exception_handler(429, _rate_limit_exceeded_handler) 
# ================================

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", " https://31cd-93-175-80-8.ngrok-free.app"],      # або точний URL фронтенду, наприклад "http://localhost:5173"
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

register_exception_handlers(app)
register_routers(app=app)




# if settings.debug:
  #DEV section
app.include_router(dev_tools.router)
  #DEV section




@app.get("/")
async def root():
    return {"message": "CryptoCases backend is alive"}

