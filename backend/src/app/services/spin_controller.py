# services/spin_controller.py
import hmac
import hashlib

from itertools import accumulate
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Dict, Union


from app.db.models.player import PlayerStat
from app.db.models.player import SpinLog
from app.db.models.case_config import CaseConfig, TierConfig, RewardItem
from app.services.risk_guard import ensure_reserve_and_limits
from app.services.rate_cache import rate_cache
from app.services.fairness_service import FairnessService
from app.schemas.case import CaseOpenResponse, PrizeItem

async def spin(user_id:int, data_for_spin: Dict[str,Union[str,int]]) -> CaseOpenResponse:
    # 1. Precheck reserve happens inside risk_guard later
    
    # 2. Commit→reveal
    case_id, client_seed, nonce, server_seed_id = data_for_spin
    # ss = await ServerSeed.get_motor_collection().find_one_and_update(
    #     {
    #         "_id":PydanticObjectId(server_seed_id),
    #         "used": False,
    #         "awner_id": user_id
    #     },
    #     {"$set":{"used": True}},
    #     return_document=ReturnDocument.AFTER
    # )
    # if not ss:
    #     raise HTTPException(503, "no_server_seed")
    # ss.used = True
    # await ss.save()
    seed_doc = await FairnessService.reveal_and_verify(commit_id=server_seed_id, user_id=user_id)
    server_seed = seed_doc.seed
    
    key = bytes.fromhex(server_seed)
    msg = f"{client_seed}:{nonce}".encode()
    raw = hmac.new(key, msg, hashlib.sha256).digest()
    roll = int.from_bytes(raw[:4], "big") / 2**32

    # 3. Load config & player
    cfg: CaseConfig = await CaseConfig.find_one(CaseConfig.case_id == case_id)
    if not cfg:
        raise HTTPException(404, "invalid_case")
    ps = await PlayerStat.find_one(PlayerStat.user_id == user_id)
    if not ps:
        ps = PlayerStat(user_id=user_id)
    
    # 4. Soft-pity
    bonus_before = 0.0
    if ps.fail_streak >= cfg.pity_after:
        bonus_before = min((ps.fail_streak - cfg.pity_after + 1)*0.02, 0.20)
    roll_adj = max(0.0, roll - bonus_before)

    # 5. Weighted-tier
    probs = [t.chance for t in cfg.tiers]
    cum_t = list(accumulate(probs))
    idx_t = next(i for i,p in enumerate(cum_t) if roll_adj < p)
    tier: TierConfig = cfg.tiers[idx_t]

    # 6. Weighted-sub
    # нормалізуємо всередині tier
    sub_roll = (roll_adj - (cum_t[idx_t-1] if idx_t>0 else 0.0)) / tier.chance  # тут можеш взяти новий u2 = (roll_adj - lower_bound_tier)/(tier_weight)
    sub_probs = [r.sub_chance for r in tier.rewards]
    cum_r = list(accumulate(sub_probs))
    idx_r = next(i for i,p in enumerate(cum_r) if sub_roll < p)
    reward: RewardItem = tier.rewards[idx_r]

    prize_amount = reward.coin_amount.amount
    rate = await rate_cache.get_rate(reward.coin_amount.coin.id)
    payout_in_usd = prize_amount * rate

    # 7. RiskGuard
    await ensure_reserve_and_limits(cfg.price_usd, payout_in_usd)

    # 8. Update player stat
    if reward.sub_chance >= 0.999:  # treat as common vs rare by name if needed
        ps.fail_streak += 1
    else:
        ps.fail_streak = 0
    bonus_after = min((ps.fail_streak - cfg.pity_after + 1)*0.02, 0.20)
    ps.rtp_session += payout_in_usd / cfg.price_usd
    ps.net_loss += cfg.price_usd - payout_in_usd
    await ps.save()

    # 9. Log spin
    await SpinLog(
        user_id=user_id,
        case_id=case_id,
        server_seed_id=server_seed_id,
        server_seed_hash=seed_doc.hash,
        client_seed=client_seed,
        nonce=nonce,
        hmac_value=raw,
        raw_roll=roll,
        table_id=cfg.odds_version,
        odds_version=cfg.odds_version,
        case_tier=tier.name,
        prize_id=reward.coin_amount.coin.id,
        stake=cfg.price_usd,
        payout=prize_amount,
        payout_usd=payout_in_usd,
        pity_before=bonus_before,
        pity_after=bonus_after,
        rtp_session=ps.rtp_session,
        created_at=datetime.now(timezone.utc),
    ).insert()
    
    return CaseOpenResponse(
        server_seed=server_seed,
        table_id=cfg.odds_version,
        odds_version=cfg.odds_version,
        prize= PrizeItem(
            coin_amount=reward.coin_amount.to_storage(),
            usd_value=str(payout_in_usd)
        ),
        payout=prize_amount,
        fail_streak=ps.fail_streak
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
