"""AssetRegistry – contract + decimals per coin & chain.

Loads **data/asset_registry.json** once at startup and provides helpers for
contract look‑up, decimals, and quick membership checks.  No external
libraries; pure Python so it works in any environment (Django, FastAPI, plain
scripts).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Union

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class AssetRegistry:
    """Singleton‑style access to asset‑level data."""

    _assets: Dict[str, Dict[str, Union["_AssetEntry","_NativeEntry"]]] = dict()

    # ------------------------------------------------------------------
    # Loader
    # ------------------------------------------------------------------

    @classmethod
    def load_from_file(cls, path: Path | str) -> None:
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))

        cls._assets = {}
        for coin_id, data in raw.items():
            coin_key = coin_id.upper()

            # Якщо у data є ключи 'symbol' і 'type', вважаємо, що це нативна монета
            if isinstance(data, dict) and "symbol" in data and "type" in data:
                cls._assets[coin_key] = {"NATIVE" :_NativeEntry(data.get("decimals", 0))}
            else:
                # Інакше очікуємо, що data — це мапа chain → { contract, decimals, ... }
                cls._assets[coin_key] = {
                    chain.upper(): _AssetEntry(chain.upper(), cfg)
                    for chain, cfg in data.items()
                }

    # ------------------------------------------------------------------
    # Access helpers
    # ------------------------------------------------------------------

    @classmethod
    def is_supported(cls, coin_id: str, chain: str) -> bool:
        normalize_coin_id = coin_id.upper()
        normalize_chain_id = chain.upper()
        if normalize_chain_id == "NATIVE":
            print(normalize_coin_id, "in assets:", normalize_coin_id in cls._assets)
            return normalize_coin_id in cls._assets
        return normalize_chain_id in cls._assets.get(normalize_coin_id, {})

    @classmethod
    def get_contract(cls, coin_id: str, chain: str) -> Optional[str]:
        try:
            asset = cls._assets[coin_id.upper()][chain.upper()]
            if isinstance(asset, _NativeEntry):
                return asset.contract # type: ignore
            else:
                return None
        except KeyError:
            return None

    @classmethod
    def get_decimals(cls, coin_id: str, chain: str | None) -> int:
        try:
            if chain is None:
                return cls._assets["TETHER"]["ERC20"].decimals
            elif chain.upper() == "NATIVE": 
                return cls._assets[coin_id.upper()]["NATIVE"].decimals
            else:
                return cls._assets[coin_id.upper()][chain.upper()].decimals
        except KeyError:
            return 18  # safe fallback

    # Debug ------------------------------------------------------------
    @classmethod
    def __repr__(cls) -> str:  # pragma: no cover
        return f"AssetRegistry(coins={len(cls._assets)})"


# ---------------------------------------------------------------------------
# Internal holder – not exported
# ---------------------------------------------------------------------------

class _AssetEntry:
    __slots__ = ("chain", "contract", "decimals")

    def __init__(self, chain: str, raw: Dict[str, str | int]):
        self.chain: str = chain.upper()
        self.contract: str = str(raw["contract"]).lower()
        self.decimals: int = int(raw["decimals"])

    def __repr__(self) -> str:  # pragma: no cover
        return f"_AssetEntry(chain={self.chain}, contract={self.contract}, decimals={self.decimals})"
    
    
class _NativeEntry:
    __slots__ = ("decimals")

    def __init__(self,  decimals: str | int):
        self.decimals: int = int(decimals)

    def __repr__(self) -> str:  # pragma: no cover
        return f"_NativeEntry(decimals={self.decimals})"