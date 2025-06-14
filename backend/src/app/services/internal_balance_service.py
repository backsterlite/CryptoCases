from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone
from typing import List, Tuple, Optional
from motor.motor_asyncio import AsyncIOMotorClientSession

from beanie import PydanticObjectId

from app.db.models.internal_balance import InternalBalance
from app.db.init_db import DataBase
from app.services.rate_cache import rate_cache
from app.services.case_service import CaseService
from app.config.coin_registry import CoinRegistry
from app.models.coin import CoinAmount
from app.exceptions.balance import BalanceTooLow
from app.utils import coin_keys

class InternalBalanceService:
    """
    Service for all internal‐balance operations.
    Can adjust balances either standalone or inside a transaction session.
    """
    
    @staticmethod
    async def get_balance(user_id: int, network: str | None, coin: str) -> Decimal:
        coin = coin_keys.to_id(coin)
        rec = await InternalBalance.find_one(
            InternalBalance.user_id == user_id,
            InternalBalance.coin == coin,
            InternalBalance.network==network
        )
        if not rec:
            # Initialize if absent
            rec = InternalBalance(user_id=user_id, network=network, coin=coin)
            await rec.insert()
        return rec.balance

    @staticmethod
    async def list_wallets(user_id: int) -> list[InternalBalance]:
        return await InternalBalance.find(InternalBalance.user_id == user_id).to_list()

    @classmethod
    async def adjust_balance(
        cls,
        user_id: int,
        coin: str,
        network: Optional[str],
        delta: Decimal,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """
        Increment (delta > 0) or decrement (delta < 0) the internal balance.
        If `delta < 0`, only deduct if the existing balance >= |delta|.
        If `delta > 0`, just add (upsert creates a doc if needed).
        In both cases, if `session` is given, run inside that transaction.
        """
        coin = coin_keys.to_id(coin)
        base_filter = {
            "user_id": user_id,
            "coin": coin,
            "network": network
        }

        if delta < 0:
            # For a debit, require existing balance >= |delta|. No upsert.
            debit_filter = {
                **base_filter,
                "$expr": {"$gte": ["$balance", abs(delta)]}
            }
            result = await InternalBalance.get_motor_collection().update_one(
                debit_filter,
                {"$inc": {"balance": delta}},
                upsert=False,
                session=session
            )
            if result.matched_count == 0:
                raise BalanceTooLow(f"Not enough {coin} balance to deduct {abs(delta)}")
        else:
            # For a credit (delta > 0), upsert if no document exists.
            await InternalBalance.get_motor_collection().update_one(
                base_filter,
                {"$inc": {"balance": delta}},
                upsert=True,
                session=session
            )
    
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
        user_wallets = await InternalBalanceService.list_wallets(user_id=user_id)
        total = Decimal("0")
        
        for curr_wallet in user_wallets:
            coin = (CoinRegistry.get(coin_keys.to_symbol(curr_wallet.coin)))
            if not coin:
                continue
            
            rate = await rate_cache.get_rate(coin.coingecko_id)
            amount_in_usd = curr_wallet.balance * rate
            total += amount_in_usd
        
        return str(total.quantize(Decimal("1.00"), rounding=ROUND_DOWN))
    

    @staticmethod
    async def create_wallet_if_needed(user_id: int, coin_id: str, network: str | None) -> None:
        user_wallet = await InternalBalance.find_one(
            {"user_id": user_id, "coin": coin_id, "network": network}
            )
        if not user_wallet:
            new_wallet = InternalBalance (
                user_id=user_id,
                coin=coin_id,
                network=network,
                balance=Decimal("0")
            )

    @staticmethod
    async def try_charge_user_for_case(user_id: int, case_id: str) -> bool:
        from app.config.settings import settings
        case = await CaseService.get_case_by_id(case_id)
        case_price = case["price_usd"]
        user_wallets = await InternalBalanceService.list_wallets(user_id)
        for wallet in user_wallets:
            if wallet.coin in settings.GLOBAL_USD_WALLET_ALIAS \
            and wallet.balance >= case_price:
                
                await InternalBalanceService.adjust_balance(
                    user_id=user_id,
                    coin=wallet.coin,
                    network=wallet.network,
                    delta=-case_price)
                return True
        return False