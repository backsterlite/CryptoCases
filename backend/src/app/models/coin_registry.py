from dataclasses import dataclass
from typing import Optional, Dict



@dataclass
class NetworkEntry:
    raw: str              # e.g. "ETHEREUM"
    contract: str         # contract address or ID
    type: str             # e.g. "EVM", "TRON", etc.

@dataclass
class DecimalEntry:
    raw: str              # original network name
    decimal_place: int

@dataclass
class NormalizedCoin:
    coin_symbol: str
    coin_name: str
    coin_thumb: Optional[str]
    coin_contract_addresses: Dict[str, NetworkEntry]  # key = code like "ERC20"
    coin_decimals: Dict[str, DecimalEntry]            # key = code like "ERC20"
    coingecko_id: str
    is_native: bool
    native_network: Optional[str]