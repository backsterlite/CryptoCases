#!/usr/bin/env python3
"""
build_chain_registry.py
========================
Generate `data/chain_registry.json` by merging auto-discovered chain data
from ChainList with manual overrides.

For each network in `data/network_map.json`, fetch the matching chain entry
from https://chainid.network/chains.json using its `shortName` or `chain`
field. Extract the following fields:
  - `type` (from network_map)
  - `chain_id` (the numerical chainId)
  - `rpc` (list of public RPC URLs)
  - `native_coin` (symbol of native currency)

Then load `data/chain_overrides.json` and apply overrides (shallow merge) so
that any fields in overrides replace the auto-generated values.  Finally,
write the result to `data/chain_registry.json` with deterministic ordering.

Usage:
    python scripts/build_chain_registry.py \
        --map data/network_map.json \
        --overrides data/chain_overrides.json \
        --output data/chain_registry.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MAP = BASE_DIR / "data" / "network_map.json"
DEFAULT_OVERRIDES = BASE_DIR / "data" / "chain_overrides.json"
DEFAULT_OUTPUT = BASE_DIR / "data" / "chain_registry.json"
CHAINLIST_URL = "https://chainid.network/chains.json"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
log = logging.getLogger("build_chain_registry")

# ---------------------------------------------------------------------------
# JSON utilities
# ---------------------------------------------------------------------------

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(obj: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)

# ---------------------------------------------------------------------------
# ChainList fetch / lookup
# ---------------------------------------------------------------------------

def fetch_chainlist() -> List[Dict[str, Any]]:
    """Retrieve the full chain list from ChainList."""
    try:
        resp = requests.get(CHAINLIST_URL, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        log.error("Failed to fetch ChainList data: %s", exc)
        sys.exit(1)


def find_chain_entry(code: str, chainlist: List[Dict[str, Any]]
                     ) -> Optional[Dict[str, Any]]:
    """Match a network code to a ChainList entry by shortName or chain."""
    code_up = code.upper()
    for entry in chainlist:
        if entry.get("shortName", "").upper() == code_up:
            return entry
        if entry.get("chain", "").upper() == code_up:
            return entry
    return None

# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_registry(
    network_map: Dict[str, Dict[str, str]],
    overrides: Dict[str, Any]
) -> Dict[str, Any]:
    """Construct the chain registry dict."""
    chainlist = fetch_chainlist()
    registry: Dict[str, Any] = {}

    for raw_key, cfg in network_map.items():
        code = cfg.get("code")
        type_ = cfg.get("type")
        if not code:
            log.warning("Skipping entry %s: no code defined", raw_key)
            continue

        entry: Dict[str, Any] = {"type": type_}
        cl = find_chain_entry(code, chainlist)
        if cl:
            entry["chain_id"] = cl.get("chainId")
            entry["rpc"] = cl.get("rpc", [])
            nft = cl.get("nativeCurrency", {})
            entry["native_coin"] = nft.get("symbol")
        else:
            log.warning("No ChainList match for code '%s', leaving minimal entry", code)
            entry.update({"chain_id": None, "rpc": [], "native_coin": None})

        # apply overrides shallowly
        if code in overrides:
            for k, v in overrides[code].items():
                entry[k] = v

        registry[code] = entry

    return registry

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Build chain_registry.json")
    p.add_argument("--map", type=Path, default=DEFAULT_MAP,
                   help="Path to network_map.json")
    p.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES,
                   help="Path to chain_overrides.json")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                   help="Path to write chain_registry.json")
    args = p.parse_args()

    network_map = load_json(args.map)
    if not network_map:
        log.error("%s not found or empty", args.map)
        return 1

    overrides = load_json(args.overrides)

    registry = build_registry(network_map, overrides)
    save_json(registry, args.output)
    log.info("Written chain registry to %s (%d entries)", args.output, len(registry))
    return 0


if __name__ == "__main__":
    sys.exit(main())
