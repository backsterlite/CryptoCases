# import json
# from pathlib import Path
# from typing import Dict, Optional, Any

# BASE_DIR = Path(__file__).parent.parent
# RAW_PATH =  BASE_DIR / "data" /"raw_coin_data.json"
# NETWORK_MAP_PATH = BASE_DIR / "data" / "network_map.json"
# OUTPUT_PATH = BASE_DIR / "data" / "coin_registry.json"

# DEFAULT_DECIMALS = 18


# def load_json(path):
#     with open(path, "r") as f:
#         return json.load(f)

# def get_first_network(platforms: Dict[str,str]) -> Optional[str]:
#     for key in platforms.keys():
#         if platforms[key]:
#             return key
#     return None

# def normalize(raw_data, network_map) -> Dict[str,Any]:
#     registry = {}

#     for coin_id, data in raw_data.items():
#         coingecko_id = data.get("id")
#         symbol = data.get("symbol")
#         name = data.get("name")
#         thumb = data.get("image", {}).get("thumb")

#         platforms = data.get("platforms", {})
#         details = data.get("detail_platforms", {})

#         contract_addresses = {}
#         decimals = {}

#         for net_raw, contract in platforms.items():
#             net_std = network_map.get(net_raw.upper())
#             if not net_std:
#                 continue
#             net_code = net_std["code"]
#             net_type = net_std["type"]

#             contract_addresses[net_code] = {
#                 "raw": net_raw.upper(),
#                 "contract": contract,
#                 "type": net_type
#             }

#             detail = details.get(net_raw)
#             if detail and detail.get("decimal_place") is not None:
#                 decimals[net_code] = {
#                     "raw": net_raw.upper(),
#                     "decimal_place": detail["decimal_place"] or DEFAULT_DECIMALS
#                 }

#         is_token = bool(contract_addresses)

#         if is_token:
#             native_network = None
#         elif data.get("asset_platform_id"):
#             native_network = data.get("asset_platform_id").upper()
#         elif get_first_network(platforms=platforms):
#             native_network = get_first_network(platforms=platforms).upper()
#         else:
#             native_network = name.upper()

#         registry[coin_id.upper()] = {
#             "coin_symbol": symbol,
#             "coin_name": name,
#             "coin_thumb": thumb,
#             "coin_contract_addresses": contract_addresses,
#             "coin_decimals": decimals,
#             "coingecko_id": coingecko_id,
#             "is_native": not is_token,
#             "native_network": native_network
#         }

#     return registry

# def main():
#     raw = load_json(RAW_PATH)
#     network_map = load_json(NETWORK_MAP_PATH)
#     result = normalize(raw, network_map)

#     with open(OUTPUT_PATH, "w") as f:
#         json.dump(result, f, indent=2)

#     print(f"Normalized {len(result)} tokens to {OUTPUT_PATH}")


# if __name__ == "__main__":
#     main()

#!/usr/bin/env python3
"""
build_coin_registry.py
======================
Produce **data/coin_registry.json** – meta only, no on‑chain tech fields.

Structure
~~~~~~~~~
```jsonc
{
  "USD-COIN": {
    "symbol": "usdc",
    "name": "USD Coin",
    "thumb": "https://assets.coingecko.com/...png",
    "coingecko_id": "usd-coin",
    "aliases": ["USDC"],
    "is_native": false,
    "native_network": null
  },
  ...
}
```

Input
-----
* **data/raw_coin_data.json** – full payloads (must exist).
* **data/network_map.json**   – to translate platform strings (optional, only
  needed to detect native network code).

Differences from legacy `normalize_coin_registry.py`
----------------------------------------------------
* **No** `coin_contract_addresses`, **no** `coin_decimals` – those now live in
  `asset_registry.json`.
* Adds `aliases` (upper‑case ticker duplicates).
* Keeps `is_native` + `native_network` for convenience.

CLI
---
```
python scripts/build_coin_registry.py           # overwrite
python scripts/build_coin_registry.py --list    # custom coin list
```
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from utils import check_is_native_token

# ---------------------------------------------------------------------------
# paths / logging
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA = BASE_DIR / "data" / "raw_coin_data.json"
NETWORK_MAP = BASE_DIR / "data" / "network_map.json"
COIN_REGISTRY = BASE_DIR / "data" / "coin_registry.json"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)
log = logging.getLogger("build_coin_registry")

# ---------------------------------------------------------------------------
# utils
# ---------------------------------------------------------------------------

def _slug(s: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "-", s.upper()).strip("-")


def _load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else {}


def _save_json(obj: Any, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)

# ---------------------------------------------------------------------------
# core
# ---------------------------------------------------------------------------

def first_non_empty(d: Dict[str, str]) -> Optional[str]:
    for k, v in d.items():
        if v:
            return k
    return None


def build(raw_path: Path, net_map_path: Path):
    raw = _load_json(raw_path)
    if not raw:
        log.error("%s not found – run fetch_raw_coin_data.py", raw_path)
        sys.exit(1)

    net_map = _load_json(net_map_path)

    registry: Dict[str, Any] = {}
    for coin_id, data in raw.items():
        sym = data.get("symbol")
        name = data.get("name")
        thumb = data.get("image", {}).get("thumb")
        gecko = data.get("id")

        is_native = check_is_native_token(data)
        
        raw_native = (data.get("asset_platform_id") 
                    or first_non_empty(data.get("platforms", {})) 
                    or None)
        if raw_native:
            key = _slug(raw_native)
            native_network = net_map.get(key, {}).get("code", key)
        else:
            native_network = None

        registry[coin_id.upper()] = {
            "symbol": sym,
            "name": name,
            "thumb": thumb,
            "coingecko_id": gecko,
            "aliases": [sym.upper()] if sym and sym.upper() != coin_id.upper() else [],
            "is_native": is_native,
            "native_network": native_network,
        }

    _save_json(dict(sorted(registry.items())), COIN_REGISTRY)
    log.info("coin_registry written → %s (%d coins)", COIN_REGISTRY, len(registry))

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build coin_registry.json (meta-only)")
    parser.add_argument("--raw", type=Path, default=RAW_DATA, help="path to raw_coin_data.json")
    parser.add_argument("--map", type=Path, default=NETWORK_MAP, help="path to network_map.json")
    args = parser.parse_args()
    build(args.raw, args.map)
