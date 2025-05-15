from decimal import Decimal, getcontext, InvalidOperation, ROUND_DOWN
from fastapi import HTTPException
from app.db.models.user import User
from app.exceptions.balance import BalanceTooLow
from app.services.rate_cache import rate_cache


class BalanceService:
    
    @staticmethod
    async def get_overall_balance_by_usd(user_id: int) -> str:
        user = await User.find_one(User.user_id==user_id)
        total = Decimal("0")
        for coin_id, nets in user.wallets.items():
            print(f"coin_id: {coin_id}")
            rate = await rate_cache.get_rate(coin_id)
            if rate == Decimal("0"): 
                continue
            for amount_str in nets.values():
                total += Decimal(amount_str) * rate
        
        return str(total.quantize(Decimal("1.00"), rounding=ROUND_DOWN))