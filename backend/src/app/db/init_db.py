from beanie import init_beanie
import motor.motor_asyncio
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


async def init_db():
    from app.config.settings import settings
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
    db = client.get_database(settings.mongo_db_name, codec_options=codec_options)
    await init_beanie(database=db, document_models=[
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
