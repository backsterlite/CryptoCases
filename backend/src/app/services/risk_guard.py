# services/risk_guard.py
from app.db.models.player import CapPool
from fastapi import HTTPException
import math

async def ensure_reserve_and_limits(stake: float, payout: float):
    pool = await CapPool.get("main")
    # 1. Cap-pool
    reserve_required = payout
    if pool.balance < reserve_required:
        raise HTTPException(503, "reserve_low")

    # 2. Max-payout
    if payout > pool.max_payout:
        raise HTTPException(400, "payout_exceeds_max")

    # 3. σ-buffer check
    # припускаємо, що pool.sigma_buffer = 4σ
    if pool.balance < pool.sigma_buffer:
        raise HTTPException(503, "maintenance")

    # якщо все добре — оновимо баланс
    pool.balance += stake * 0.05  # 5% share
    pool.balance -= payout
    await pool.save()
