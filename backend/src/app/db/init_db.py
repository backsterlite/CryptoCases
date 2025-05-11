from beanie import init_beanie
import motor.motor_asyncio

from app.config.settings import settings
from app.db.models.user import User  


async def init_db():
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    await init_beanie(database=db, document_models=[User])
