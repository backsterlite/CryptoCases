from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClientSession
from typing import AsyncGenerator

from .init_db import DataBase

class TransactionManager:
    
    
    @asynccontextmanager
    async def __call__(self) -> AsyncGenerator[AsyncIOMotorClientSession,None]:
        async with DataBase.start_transaction() as session:
            yield session