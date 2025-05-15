import pytest
import hmac, hashlib
from decimal import Decimal
from app.services.spin_controller import spin
from app.db.models.player import ServerSeed, PlayerStat, CapPool, SpinLog
from app.db.models.case_config import CaseConfig, TierConfig, RewardItem
from app.models.coin import CoinAmount, Coin
from beanie import PydanticObjectId

@pytest.mark.anyio
async def test_spin_deterministic(db):
    # підготуємо seed і config
    raw = b"\x01"*32
    hex_s = raw.hex()
    hash0 = hashlib.sha256(raw).hexdigest()
    ss = ServerSeed(seed=hex_s, hash=hash0, owner_id="42")
    await ss.insert()
    cfg = CaseConfig(
        case_id="case_test",
        price_usd=Decimal("10"),
        tiers= [
            TierConfig(
            name="common",
            chance=1,
            rewards = [
                RewardItem(
                    coin_id="shiba-inu",
                    amount="1",
                    network="ERC20",
                    sub_chance=1
                )
            ]
            )
        ],#
        pity_after=0, 
        pity_bonus_tier="",
        global_pool_usd=10, pool_reset_interval="24h",
        odds_versions=[{"version":"v1","sha256":hash0,"url":""}]
    )
    await cfg.insert()
    await CapPool(id="main", balance=1000, sigma_buffer=100, max_payout=100).insert()

    # spin
    resp1 = await spin(42, {"case_id":"case_test","client_seed":"a","nonce":0,"server_seed_id":str(ss.id)})
    resp2 = await spin(42, {"case_id":"case_test","client_seed":"a","nonce":0,"server_seed_id":str(ss.id)})
    assert resp1.prize == resp2.prize
    # перевіримо RAW-лог
    log = await SpinLog.find_one({"user_id":"42","case_id":"case_test"})
    assert log.raw_roll == pytest.approx(log.raw_roll)
