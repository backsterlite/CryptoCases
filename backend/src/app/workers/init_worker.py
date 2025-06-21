from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config.settings import Settings
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

async def init_worker_db():
    """
    Ініціалізація підключення до MongoDB для Celery workers
    """
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    
    await init_beanie(
        database=db,
        document_models=[
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
        ]
    )
    
    return client

def get_db_client():
    """
    Отримання клієнта MongoDB для Celery workers
    """
    return AsyncIOMotorClient(settings.mongo_uri) 