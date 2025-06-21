# services/spin_controller.py
import hmac
import hashlib

from itertools import accumulate
from datetime import datetime, timezone
from typing import Dict, Union, Optional
from decimal import Decimal

from fastapi import HTTPException
from beanie import PydanticObjectId


from app.db.models.player import PlayerStat
from app.db.models.player import SpinLog
from app.db.models.case_config import CaseConfig, TierConfig, RewardItem
from app.services.risk_guard import ensure_reserve_and_limits
from app.services.rate_cache import rate_cache
from app.services.fairness_service import FairnessService
from app.schemas.case import CaseOpenResponse, PrizeItem, CaseOpenRequest
from app.core.config.settings import Settings
from app.core.config.settings import get_settings

settings: Settings = get_settings()

ZERO = Decimal("0")
STEP = Decimal("0.02")
MAX_BONUS = Decimal("0.20")
async def spin(user_id:int, data_for_spin: CaseOpenRequest) -> CaseOpenResponse:

    seed_doc = await FairnessService.reveal_and_verify(
        commit_id=PydanticObjectId(data_for_spin.server_seed_id),
        user_id=user_id)
    server_seed = seed_doc.seed
    
    key = bytes.fromhex(server_seed)
    msg = f"{data_for_spin.client_seed}:{data_for_spin.nonce}".encode()
    raw = hmac.new(key, msg, hashlib.sha256).digest()
    roll = Decimal.from_float(int.from_bytes(raw[:4], "big") / 2**32)

    # 3. Load config & player
    cfg: Optional[CaseConfig] = await CaseConfig.find_one(CaseConfig.case_id == data_for_spin.case_id)
    if not cfg:
        raise HTTPException(404, "invalid_case")
    ps = await PlayerStat.find_one(PlayerStat.user_id == user_id)
    if not ps:
        ps = PlayerStat(user_id=user_id)
    
    # 4. Soft-pity
    bonus_before = ZERO
    if ps.fail_streak >= cfg.pity_after:
        diff = ps.fail_streak - cfg.pity_after + 1
        potential = diff * STEP
        bonus_before = min(potential, MAX_BONUS)
    roll_adj = max(ZERO, roll - bonus_before) 

    # 5. Weighted-tier
    probs = [t.chance for t in cfg.tiers]
    cum_t = list(accumulate(probs))
    idx_t = next(i for i,p in enumerate(cum_t) if roll_adj < p)
    tier: TierConfig = cfg.tiers[idx_t]

    # 6. Weighted-sub
    # нормалізуємо всередині tier
    sub_roll = (roll_adj - (cum_t[idx_t-1] if idx_t > 0 else ZERO)) / tier.chance  # тут можеш взяти новий u2 = (roll_adj - lower_bound_tier)/(tier_weight)
    sub_probs = [r.sub_chance for r in tier.rewards]
    cum_r = list(accumulate(sub_probs))
    idx_r = next(i for i,p in enumerate(cum_r) if sub_roll < p)
    reward: RewardItem = tier.rewards[idx_r]
    reward.network = None if reward.coin_id in settings.GLOBAL_USD_WALLET_ALIAS else reward.network

    prize_amount = Decimal(reward.amount)
    rate = await rate_cache.get_rate(reward.coin_id)
    payout_in_usd = prize_amount * rate

    # 7. RiskGuard
    await ensure_reserve_and_limits(cfg.price_usd, payout_in_usd)

    # 8. Update player stat
    if reward.sub_chance >= 0.999:  # treat as common vs rare by name if needed
        ps.fail_streak += 1
    else:
        ps.fail_streak = 0
        
    bonus_after = ZERO
    if ps.fail_streak >= cfg.pity_after:
        diff_after = ps.fail_streak - cfg.pity_after + 1
        potential_after = diff_after * STEP
        bonus_after = min(potential_after, MAX_BONUS)
        
    ps.rtp_session = ps.rtp_session + (payout_in_usd / cfg.price_usd)
    ps.net_loss += cfg.price_usd - payout_in_usd
    await ps.save()
    odds_version = cfg.odds_versions[-1].version
    # 9. Log spin
    spin_log =  SpinLog(
        user_id=user_id,
        case_id=data_for_spin.case_id,
        server_seed_id=data_for_spin.server_seed_id,
        server_seed_hash=seed_doc.hash,
        server_seed_seed=server_seed,
        client_seed=data_for_spin.client_seed,
        nonce=data_for_spin.nonce,
        hmac_value=raw,
        raw_roll=roll,
        table_id=odds_version,
        odds_version=odds_version,
        case_tier=tier.name,
        prize_id=reward.coin_id,
        stake=cfg.price_usd,
        payout=prize_amount,
        payout_usd=payout_in_usd,
        pity_before=bonus_before,
        pity_after=bonus_after,
        rtp_session=ps.rtp_session,
        created_at=datetime.now(timezone.utc),
    )
    await spin_log.insert()
    return CaseOpenResponse(
        server_seed=server_seed,
        table_id=odds_version,
        odds_version=odds_version,
        prize= PrizeItem(
            coin_amount=(reward.coin_id, reward.network, reward.amount),
            usd_value=str(payout_in_usd),
            reward_tier=tier.name
        ),
        payout=prize_amount,
        fail_streak=ps.fail_streak,
        spin_log_id=spin_log.id
    )
    # return {
    #     "server_seed": ss.seed,
    #     "table_id": cfg.odds_version,
    #     "odds_version": cfg.odds_version,
    #     "prize": {
    #         "coin_amount": reward.coin_amount.to_storage(),
    #         "usd_value": str(payout_in_usd),
    #     },
    #     "payout": prize_amount,
    #     "fail_streak": ps.fail_streak,
    # }
