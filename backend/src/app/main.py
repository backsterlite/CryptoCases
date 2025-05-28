from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.api.routers import register_routers
from app.exceptions import register_exception_handlers
from app.core.bootstrap import bootstrap
from app.config.settings import settings


#DEV section
from app.dev import dev_tools
#DEV section



@asynccontextmanager
async def lifespan(app: FastAPI):
    await bootstrap.run()
    yield 
    await bootstrap.stop()

app = FastAPI(title="CryptoCases API", lifespan=lifespan, debug=settings.debug)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],      # або точний URL фронтенду, наприклад "http://localhost:5173"
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

register_exception_handlers(app)
register_routers(app=app)




if settings.debug:
  #DEV section
  app.include_router(dev_tools.router)
  #DEV section




@app.get("/")
async def root():
    return {"message": "CryptoCases backend is alive"}

