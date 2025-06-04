from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .mongo_codec import codec_options


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

    @classmethod
    async def init_db(cls):
        from app.config.settings import settings
        cls._client = AsyncIOMotorClient(settings.mongo_uri)
        cls._db = cls._client.get_database(settings.mongo_db_name, codec_options=codec_options)
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
