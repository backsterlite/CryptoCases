from beanie import init_beanie
import motor.motor_asyncio


from app.db.models import (
    user,
    player,
    case_config,
    case_log,
    withdrawal
)


async def init_db():
    from app.config.settings import settings
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
    await init_beanie(database=db, document_models=[
        user.User,
        player.CapPool,
        player.PlayerStat,
        player.ServerSeed,
        player.SpinLog,
        case_config.CaseConfig,
        case_log.CaseLog,
        withdrawal.WithdrawalLog
        ])
