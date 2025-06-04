from typing import Dict, Optional
from app.schemas.wallet import UserTokenWallet, UserWalletsGrouped
from app.services.internal_balance_service import InternalBalanceService
from app.config.coin_registry import CoinRegistry, CoinMeta


async def group_wallets_by_coin(user_id: int) -> UserWalletsGrouped:
    result: Dict[str,UserTokenWallet] = dict()
    user_wallets =  await InternalBalanceService.list_wallets(user_id)
    for wallet in user_wallets:
        coin: Optional[CoinMeta] = CoinRegistry.get(wallet.coin)
        if not coin:
            continue
        result[wallet.coin] = UserTokenWallet(
            coin=coin,
            balance={wallet.network: wallet.balance}
            
        )
        
    return UserWalletsGrouped(result)