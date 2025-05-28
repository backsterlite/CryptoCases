# scripts/collect_stats.py

import asyncio
from collections import Counter, defaultdict
from decimal import Decimal
import json
import csv
import os
import hmac
import hashlib

from typing import Optional
from itertools import accumulate

from app.db.init_db import init_db                              # :contentReference[oaicite:1]{index=1}
from app.db.models.case_config import CaseConfig         # :contentReference[oaicite:2]{index=2}
from app.services.rate_cache import rate_cache           # :contentReference[oaicite:3]{index=3}  # :contentReference[oaicite:4]{index=4}

# Кількість спінів на кейс
N = 1000
ZERO = Decimal("0")
STEP = Decimal("0.02")
MAX_BONUS = Decimal("0.20")

async def main():
    # 1) Ініціалізація БД/Beanie
    await init_db()

    # 2) Зчитуємо всі курси з кешу
    with open("/app/data/rate_cache.json", "r") as f:
        rates = json.load(f)
    rates = {k: Decimal(v) for k,v in rates.items()}
    print(rates)
    
    

    # 3) Завантажуємо всі кейси
    cases = await CaseConfig.find_all().to_list()
    
    # Папка для результатів
    os.makedirs("/app/data/stats_output", exist_ok=True)

    for case in cases:
        stats = {
            "spent": Decimal("0"),
            "received": Decimal("0"),
            "by_tier": Counter(),
            "by_item": Counter(),
        }

        # 4) Симулюємо N спінів
        client_seed = os.urandom(16).hex()
        for i in range(N):
            # підготуємо фейковий запит
            server_seed = generate_server_seed()
            nonce = i
            key = bytes.fromhex(server_seed)
            msg = f"{client_seed}:{nonce}".encode()
            raw = hmac.new(key, msg, hashlib.sha256).digest()
            roll = Decimal.from_float(int.from_bytes(raw[:4], "big") / 2**32)

            

            # 5. Weighted-tier
            probs = [t.chance for t in case.tiers]
            cum_t = list(accumulate(probs))
            idx_t = next(i for i,p in enumerate(cum_t) if roll < p)
            tier = case.tiers[idx_t]

            # 6. Weighted-sub
            # нормалізуємо всередині tier
            sub_roll = (roll - (cum_t[idx_t-1] if idx_t > 0 else ZERO)) / tier.chance  # тут можеш взяти новий u2 = (roll_adj - lower_bound_tier)/(tier_weight)
            sub_probs = [r.sub_chance for r in tier.rewards]
            cum_r = list(accumulate(sub_probs))
            idx_r = next(i for i,p in enumerate(cum_r) if sub_roll < p)
            reward = tier.rewards[idx_r]
            if reward.coin_id not in rates.keys():
                print(f"skip {reward.coin_id} coin")
                continue 
            prize_amount = Decimal(reward.amount)
            rate = rates[reward.coin_id]
            payout_in_usd = prize_amount * rate

            # Накопичуємо
            stats["spent"] += case.price_usd
            stats["received"] += payout_in_usd
            stats["by_tier"][tier.name] += 1
            stats["by_item"][reward.coin_id] += 1

        # 5) Пишемо JSON
        out_json = {
            "case_id": case.case_id,
            "spent": str(stats["spent"]),
            "received": str(stats["received"]),
            "by_tier": dict(stats["by_tier"]),
            "by_item": dict(stats["by_item"]),
            "N": N,
        }
        with open(f"/app/data/stats_output/{case.case_id}.json", "w") as f:
            json.dump(out_json, f, indent=2)

        # 6) Пишемо CSV по айтемам
        with open(f"/app/data/stats_output/{case.case_id}_items.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["item_id", "count", "empirical_chance"])
            for item, cnt in stats["by_item"].items():
                writer.writerow([item, cnt, cnt/N])

        # 7) Пишемо CSV по тиру
        with open(f"/app/data/stats_output/{case.case_id}_tiers.csv", "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["tier", "count", "empirical_chance"])
            for tier, cnt in stats["by_tier"].items():
                writer.writerow([tier, cnt, cnt/N])

        print(f"Stats for {case.case_id} written.")

def generate_server_seed():
    raw = os.urandom(32)
    hex_seed = raw.hex()
    return hex_seed
if __name__ == "__main__":
    asyncio.run(main())
