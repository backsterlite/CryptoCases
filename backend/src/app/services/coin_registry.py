from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, NoReturn, List
from app.models.coin_registry import NormalizedCoin, NetworkEntry, DecimalEntry


class CoinRegistry:
    _registry: Dict[str, NormalizedCoin] = {}

    @classmethod
    def load_from_file(cls, path: Path) -> NoReturn:
        with open(path, "r") as f:
            raw_data = json.load(f)

        cls._registry = cls._parse(raw_data)
        
    @classmethod
    def _parse(cls, raw_data) -> Dict[str,NormalizedCoin]:
        parsed = {}
        for coin_id, entry in raw_data.items():
            parsed[coin_id.upper()] = NormalizedCoin(
                coin_symbol=entry["coin_symbol"],
                coin_name=entry["coin_name"],
                coin_thumb=entry.get("coin_thumb"),
                coin_contract_addresses={
                    code: NetworkEntry(**net)
                    for code, net in entry["coin_contract_addresses"].items()
                },
                coin_decimals={
                    code: DecimalEntry(**dec)
                    for code, dec in entry["coin_decimals"].items()
                },
                coingecko_id=entry["coingecko_id"],
                is_native=entry["is_native"],
                native_network=entry["native_network"]
            )
        return parsed
    
    @classmethod
    def get(cls, coin_id: str) -> Optional[NormalizedCoin]:
        return cls._registry.get(coin_id.upper())

    @classmethod
    def get_contract(cls, coin_id: str, network: str) -> Optional[str]:
        coin = cls.get(coin_id)
        if not coin:
            return None
        entry = coin.coin_contract_addresses.get(network.upper())
        return entry.contract if entry else None

    @classmethod
    def get_decimals(cls, coin_id: str, network: str) -> Optional[int]:
        coin = cls.get(coin_id)
        if not coin:
            return None
        entry = coin.coin_decimals.get(network.upper())
        return entry.decimal_place if entry else None

    @classmethod
    def is_supported(cls, coin_id: str, network: str) -> bool:
        coin = cls.get(coin_id)
        return network.upper() in coin.coin_contract_addresses if coin else False

    @classmethod
    def get_runtime(cls, coin_id: str) -> Optional["Coin"]: # type: ignore  # noqa: F821
        from app.models.coin import Coin
        
        normalize_coin = cls.get(coin_id)
        if not normalize_coin:
            return None
        
        coin = Coin.from_registry(normalize_coin)
        return coin
    
    @classmethod
    def get_ids(cls) -> Optional[List[str]]:
        if CoinRegistry._registry:
            return [key.lower() for key in CoinRegistry._registry.keys()]
        return []
        
