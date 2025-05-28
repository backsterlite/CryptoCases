"""network_registry.py
Module responsible for loading and accessing on‑chain configuration
(networks, RPC endpoints, tokens available for deposit/withdrawal).

This layer intentionally separates operational blockchain data from the general
coin metadata stored in ``coin_registry.json``.  All services that need to know
*where* and *how* to interact with chains (DepositService, WithdrawalService,
price crawlers, etc.) should depend on this module instead of hard‑coded
settings.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional, Tuple

Operation = Literal["deposit", "withdrawal"]

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class NetworkRegistryError(RuntimeError):
    """Base‑class for registry exceptions."""


class UnknownNetworkError(NetworkRegistryError):
    """Raised when requested network code is not present in registry."""


class UnsupportedOperationError(NetworkRegistryError):
    """Raised when operation is not one of (deposit|withdrawal)."""


class UnsupportedTokenError(NetworkRegistryError):
    """Raised when requested token is not allowed for the given operation."""


# ---------------------------------------------------------------------------
# Data holders (simple dict wrappers, not full dataclasses to avoid runtime
# overhead / circular import issues inside Django context)
# ---------------------------------------------------------------------------

def _to_int(value: Any) -> int:
    try:
        return int(value)
    except Exception as exc:  # pragma: no cover
        raise ValueError(f"Cannot cast {value!r} to int") from exc


class TokenCfg:
    """Lightweight view around token entry (contract/decimals)."""

    __slots__ = ("symbol", "contract", "decimals")

    def __init__(self, raw: Mapping[str, Any]):
        self.symbol: str = raw["symbol"].upper()
        self.contract: Optional[str] = raw.get("contract") or None
        self.decimals: int = _to_int(raw["decimals"])

    # Helpful for debug / logging ------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        c = self.contract or "<native>"
        return f"TokenCfg(symbol={self.symbol}, contract={c}, decimals={self.decimals})"


class NetworkCfg:
    """Wrapper for network‑level config (rpc, type, tokens, etc.)."""

    __slots__ = (
        "code",
        "type",
        "rpc",
        "min_confirmations",
        "existence_check",
        "_deposit_tokens",
        "_withdrawal_tokens",
    )

    def __init__(self, code: str, raw: Mapping[str, Any]):
        self.code: str = code.upper()
        self.type: str = raw["type"].upper()
        self.rpc: Any = raw["rpc"]  # str | list[str]
        self.min_confirmations: int = _to_int(raw.get("min_confirmations", 0))
        self.existence_check: bool = bool(raw.get("existence_check", True))

        # Pre‑index tokens by symbol for O(1) lookup later.
        self._deposit_tokens: Dict[str, TokenCfg] = {
            t["symbol"].upper(): TokenCfg(t) for t in raw.get("deposit_tokens", [])
        }
        self._withdrawal_tokens: Dict[str, TokenCfg] = {
            t["symbol"].upper(): TokenCfg(t) for t in raw.get("withdrawal_tokens", [])
        }

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------

    def list_tokens(self, op: Operation) -> List[str]:
        if op == "deposit":
            return list(self._deposit_tokens.keys())
        if op == "withdrawal":
            return list(self._withdrawal_tokens.keys())
        raise UnsupportedOperationError(op)

    def token_cfg(self, symbol: str, op: Operation) -> TokenCfg:
        lookup = self._deposit_tokens if op == "deposit" else self._withdrawal_tokens
        try:
            return lookup[symbol.upper()]
        except KeyError as exc:
            raise UnsupportedTokenError(
                f"Token {symbol} not allowed for {op} on network {self.code}"
            ) from exc

    # Debug ----------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"NetworkCfg(code={self.code}, type={self.type}, rpc={self.rpc}, "
            f"deposit={list(self._deposit_tokens)}, withdrawal={list(self._withdrawal_tokens)})"
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class NetworkRegistry:
    """Loads *network_registry.json* and provides access helpers.

    This class is intentionally environment‑agnostic; DI frameworks or Django
    settings should create a singleton instance and pass it to services.
    """

    def __init__(self, path: str | Path):
        self._path = Path(path)
        if not self._path.exists():
            raise FileNotFoundError(self._path)

        data = json.loads(self._path.read_text())
        self._networks: Dict[str, NetworkCfg] = {
            code.upper(): NetworkCfg(code, raw) for code, raw in data.items()
        }

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------

    def get_network(self, code: str) -> NetworkCfg:
        try:
            return self._networks[code.upper()]
        except KeyError as exc:
            raise UnknownNetworkError(code) from exc

    def list_network_codes(self) -> List[str]:
        return list(self._networks.keys())

    def list_tokens(self, network_code: str, op: Operation) -> List[str]:
        return self.get_network(network_code).list_tokens(op)

    def token_cfg(self, network_code: str, symbol: str, op: Operation) -> TokenCfg:
        return self.get_network(network_code).token_cfg(symbol, op)

    # Convenience helpers --------------------------------------------------

    def is_token_allowed(self, network_code: str, symbol: str, op: Operation) -> bool:
        try:
            self.token_cfg(network_code, symbol, op)
            return True
        except NetworkRegistryError:
            return False

    # Debug ----------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"NetworkRegistry(path={self._path}, networks={len(self._networks)})"
