from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorClientSession
from .mongo_codec import codec_options

from app.core.config.settings import Settings, get_settings


from app.db.models import (
    user,
    player,
    case_config,
    case_log,
    withdrawal_log,
    internal_balance,
    deposit_log,
    external_wallet
)

class DataBase:
    _client: AsyncIOMotorClient
    _db: AsyncIOMotorDatabase
    _settings: Settings
    @classmethod
    async def init_db(cls):
        cls._settings = get_settings()
        cls._client = AsyncIOMotorClient(cls._settings.mongo_uri)
        cls._db = cls._client.get_database(cls._settings.mongo_db_name, codec_options=codec_options)
        
        await init_beanie(database=cls._db, document_models=[
            user.User,
            player.CapPool,
            player.PlayerStat,
            player.ServerSeed,
            player.SpinLog,
            case_config.CaseConfig,
            case_log.CaseLog,
            external_wallet.ExternalWallet,
            deposit_log.DepositLog,
            internal_balance.InternalBalance,
            withdrawal_log.WithdrawalLog
            ])
    @classmethod
    def get_client(cls) -> AsyncIOMotorClient:
        """
        Return a singleton Motor client to use for both
        ad‐hoc updates and transactions.
        """
        if cls._client is None:
            cls._client = DataBase._client
        return cls._client
    
    @classmethod
    @asynccontextmanager
    async def start_transaction(cls) -> AsyncIterator[AsyncIOMotorClientSession]:
        """
        Async context manager that yields a MongoDB session in a transaction.
        Usage:
            async with InternalBalanceService.start_transaction() as session:
                await InternalBalanceService.adjust_balance(..., session=session)
                await InternalBalanceService.adjust_balance(..., session=session)
        """
        client = cls.get_client()
        async with await client.start_session() as session:
            async with session.start_transaction():
                yield session