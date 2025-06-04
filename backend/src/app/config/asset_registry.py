"""AssetRegistry – contract + decimals per coin & chain.

Loads **data/asset_registry.json** once at startup and provides helpers for
contract look‑up, decimals, and quick membership checks.  No external
libraries; pure Python so it works in any environment (Django, FastAPI, plain
scripts).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class AssetRegistry:
    """Singleton‑style access to asset‑level data."""

    _assets: Dict[str, Dict[str, "_AssetEntry"]] = {}

    # ------------------------------------------------------------------
    # Loader
    # ------------------------------------------------------------------

    @classmethod
    def load_from_file(cls, path: Path | str) -> None:
        path = Path(path)
        raw = json.loads(path.read_text(encoding="utf-8"))
        cls._assets = {
            coin_id.upper(): {
                chain.upper(): _AssetEntry(chain, cfg)
                for chain, cfg in chains.items()
            }
            for coin_id, chains in raw.items()
        }

    # ------------------------------------------------------------------
    # Access helpers
    # ------------------------------------------------------------------

    @classmethod
    def is_supported(cls, coin_id: str, chain: str) -> bool:
        return chain.upper() in cls._assets.get(coin_id.upper(), {})

    @classmethod
    def get_contract(cls, coin_id: str, chain: str) -> Optional[str]:
        try:
            return cls._assets[coin_id.upper()][chain.upper()].contract
        except KeyError:
            return None

    @classmethod
    def get_decimals(cls, coin_id: str, chain: str) -> int:
        try:
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