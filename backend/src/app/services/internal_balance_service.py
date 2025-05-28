from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone
from typing import List, Tuple

from app.db.models.internal_balance import InternalBalance
from app.services.rate_cache import rate_cache
from app.models.coin import CoinAmount
from app.exceptions.balance import BalanceTooLow

class InternalBalanceService:
    @staticmethod
    async def get_balance(user_id: int, network: str, coin: str) -> Decimal:
        rec = await InternalBalance.find_one(
            (InternalBalance.user_id == user_id) & (InternalBalance.coin == coin)
        )
        if not rec:
            # Initialize if absent
            rec = InternalBalance(user_id=user_id, network=network, coin=coin)
            await rec.insert()
        return rec.balance

    @staticmethod
    async def list_balances(user_id: int) -> list[InternalBalance]:
        return await InternalBalance.find(InternalBalance.user_id == user_id).to_list()

    @staticmethod
    async def adjust_balance(user_id: str, coin: str, amount: Decimal) -> InternalBalance:
        # Atomic upsert with increment
        new = await InternalBalance.get_motor_collection().find_one_and_update(
            {"user_id": user_id, "coin": coin},
            {"$inc": {"balance": str(amount)}, "$set": {"updated_at": datetime.now(timezone.utc)}},
            upsert=True,
            return_document=True
        )
        return InternalBalance(**new)
    
    @staticmethod
    async def deduct_usd_amount(user_id: str, amount_usd: Decimal) -> None:
        """
        Deducts the specified USD amount from the user's internal balances across all coins.
        Withdraws from balances starting with the highest USD equivalent until amount_usd is covered.
        """
        collection = InternalBalance.get_motor_collection()
        client = collection.database.client
        async with await client.start_session() as session:
            async with session.start_transaction():
                
                # Load all balances
                balances: List[InternalBalance] = await collection.find(
                    {"user_id" == user_id},
                    session=session).to_list(None)
                # Compute USD equivalents
                usd_entries: List[Tuple[InternalBalance, Decimal]] = []
                total_usd = Decimal('0')
                for b in balances:
                    # Get rate
                    rate = await rate_cache.get_rate(b.coin)
                    # get CoinAmount instance
                    coin_amount = CoinAmount.from_str(
                        coin_id=b.coin,
                        network=b.network,
                        amount_str=str(b.balance)
                    )
                    # Convert entire balance to USD
                    bal_usd = coin_amount.to_usd(rate)
                    if bal_usd > 0:
                        usd_entries.append((b, bal_usd))
                        total_usd += bal_usd
                if total_usd < amount_usd:
                    raise BalanceTooLow()
                # Sort descending by USD value
                usd_entries.sort(key=lambda x: x[1], reverse=True)

                remaining = amount_usd
                # Deduct from highest USD equivalent balances
                for b, bal_usd in usd_entries:
                    if remaining <= 0:
                        break
                    rate = await rate_cache.get_rate(b.coin)
                    if bal_usd <= remaining:
                        # Deduct entire coin balance
                        deduct_usd = bal_usd
                        deduct_coin = b.balance
                        b.balance = Decimal('0')
                    else:
                        # Partial deduction
                        deduct_usd = remaining
                        # Convert USD back to coin amount
                        deduct_coin = CoinAmount.amount_from_usd(
                            coin_id=b.coin,
                            network=b.network,
                            value_in_usd=remaining,
                            rate=rate
                            )
                        b.balance -= deduct_coin
                    remaining -= deduct_usd
                    # Save updated balance
                    await collection.update_one(
                        {"_id": b.id},
                        {"$set": {"balance":b.balance, "updated_at": datetime.now(timezone.utc)}},
                        session=session
                    )

                # Ensure no rounding issues remain
                if remaining > Decimal('0'):
                    raise RuntimeError('Помилка при списанні: залишок не обнулено')
    
    @staticmethod
    async def get_overall_balance_by_usd(user_id: int) -> str:
        user_wallets = await InternalBalanceService.list_balances(user_id=user_id)
        total = Decimal("0")
        
        for curr_wallet in user_wallets:
            rate = await rate_cache.get_rate(curr_wallet.coin)
            amount_in_usd = curr_wallet.balance * rate
            total += amount_in_usd
        
        return str(total.quantize(Decimal("1.00"), rounding=ROUND_DOWN))
        
