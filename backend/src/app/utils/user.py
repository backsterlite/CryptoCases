from typing import Dict
from app.models.coin import CoinAmount
from app.schemas.user_wallets import UserTokenWallet
from app.services.coin_registry import CoinRegistry


def group_wallets_by_coin(wallets: Dict[str, Dict[str, str]]) -> Dict[str,UserTokenWallet]:
    result = dict()
    for symbol, network_dict in wallets.items():
        coin = CoinRegistry.get_runtime(symbol)
        if not coin:
            continue  # або log warning
        result[symbol] = UserTokenWallet(
            coin=coin,
            balances=network_dict
        )
    return result