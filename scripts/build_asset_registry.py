#!/usr/bin/env python3
"""
build_asset_registry.py
=======================
Create **data/asset_registry.json** in the form

```jsonc
{
  "USD-COIN": {
    "POLYGON-POS": {"contract": "0x2791...", "decimals": 6},
    "ARBITRUM-ONE": {"contract": "0xFF97...", "decimals": 6}
  },
  ...
}
```

Input files
-----------
* **data/raw_coin_data.json** – full payloads from Coingecko (must exist).
* **data/network_map.json**   – mapping of raw platform strings to `{code,type}`.

Rules
-----
1. Use `detail_platforms` if present (Coingecko v3), else fallback to `platforms`.
2. Canonical *network code* comes from `network_map.json[slug(raw)].code`;
   if that code is `UNKNOWN`, the entry is **skipped** and reported.
3. If `decimals` is missing or zero, default to **18**.
4. Existing `asset_registry.json` is merged **in‑place** (never clobbers manual
   decimals fixes) unless `--force` is passed.

CLI
---
```
python scripts/build_asset_registry.py              # incremental
python scripts/build_asset_registry.py --force      # rebuild
```
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict

# ---------------------------------------------------------------------------
# paths / logging
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw_coin_data.json"
NETWORK_MAP = BASE_DIR / "data" / "network_map.json"
ASSET_REGISTRY = BASE_DIR / "data" / "asset_registry.json"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
log = logging.getLogger("build_asset_registry")

# ---------------------------------------------------------------------------
# util
# ---------------------------------------------------------------------------

def _slug(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", s.upper()).strip("-")


def _load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else {}


def _save_json(obj: Any, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    tmp.replace(path)

# ---------------------------------------------------------------------------
# main logic
# ---------------------------------------------------------------------------

def build(force: bool = False):
    raw_data = _load_json(RAW_DATA)
    if not raw_data:
        log.error("%s not found – run fetch_raw_coin_data.py first", RAW_DATA)
        sys.exit(1)

    net_map: Dict[str, Dict[str, str]] = _load_json(NETWORK_MAP)
    if not net_map:
        log.error("%s not found – run build_network_map.py first", NETWORK_MAP)
        sys.exit(1)

    registry: Dict[str, Dict[str, Dict[str, Any]]] = {} if force else _load_json(ASSET_REGISTRY)

    skipped_unknown = 0
    added = 0

    for coin_id, payload in raw_data.items():
        platforms = payload.get("detail_platforms") or payload.get("platforms") or {}
        if not platforms:
            continue  # native coin w/o contract
        coin_entry = registry.setdefault(coin_id, {})
        for raw_platform, detail in platforms.items():
            key = _slug(raw_platform)
            if key not in net_map:
                log.warning("platform '%s' missing in network_map.json (skip)", raw_platform)
                skipped_unknown += 1
                continue
            chain_code = net_map[key]["code"]
            if chain_code == "UNKNOWN":
                skipped_unknown += 1
                continue
            contract = (
                detail.get("contract_address")
                if isinstance(detail, dict)
                else detail  # old 'platforms' field is addr str or empty
            )
            if not contract:
                continue  # nothing to register
            decimals = (
                detail.get("decimal_place") if isinstance(detail, dict) else None
            )
            decimals = int(decimals) if decimals else 18
            if chain_code in coin_entry and not force:
                continue  # do not overwrite manual entry
            coin_entry[chain_code] = {"contract": contract.lower(), "decimals": decimals}
            added += 1

    _save_json(dict(sorted(registry.items())), ASSET_REGISTRY)
    log.info("asset_registry written: %s (added %d, skipped %d)", ASSET_REGISTRY, added, skipped_unknown)

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build asset_registry.json from Coingecko data")
    parser.add_argument("--force", action="store_true", help="recreate from scratch, drop overrides")
    args = parser.parse_args()
    build(force=args.force)
