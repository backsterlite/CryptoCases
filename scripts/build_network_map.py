#!/usr/bin/env python3
"""
build_network_map.py
====================
Generate / extend `data/network_map.json` using the *platform* strings found
in `data/raw_coin_data.json` (downloaded from Coingecko).

*   Already‑known entries are preserved.
*   New platforms are matched against **chainlist.org**; if a match is found we
    fill `code` with the chainlist `shortName` (upper‑case) and `type` with
    either "EVM" or the chainlist `type`.  If no match, we add a skeleton
    record so that a human can complete it later:
    `{"code": "UNKNOWN", "type": "UNKNOWN"}`.
*   The script never overwrites existing keys – manual edits are safe.
*   Output is always written with deterministic ordering.

Usage
-----
```bash
python scripts/build_network_map.py           # incremental update
python scripts/build_network_map.py --force   # rebuild from scratch
```
CLI flags
~~~~~~~~~
--source   path to raw_coin_data.json  (default: data/raw_coin_data.json)
--map      path to network_map.json    (default: data/network_map.json)
--force    ignore existing map, start empty
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

import requests

# ---------------------------------------------------------------------------
# const / cfg
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = BASE_DIR / "data" / "raw_coin_data.json"
DEFAULT_MAP = BASE_DIR / "data" / "network_map.json"
CHAINLIST_URL = "https://chainid.network/chains.json"

logger = logging.getLogger("build_network_map")
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)

session = requests.Session()

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _slug(name: str) -> str:
    """Convert arbitrary platform string to canonical key (UPPER‑KEBAB)."""
    return re.sub(r"[^A-Z0-9]+", "-", name.upper()).strip("-")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text()) if path.exists() else {}


def _save_json(obj: Any, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    tmp.replace(path)


def _fetch_chainlist() -> List[Dict[str, Any]]:
    try:
        resp = session.get(CHAINLIST_URL, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning("cannot fetch chainlist – %s", exc)
        return []


def _match_chain(raw: str, chainlist: List[Dict[str, Any]]) -> tuple[str, str]:
    """Return (code, type) best guess for `raw` platform name."""
    raw_up = raw.upper()
    for entry in chainlist:
        names = {entry.get("name", "").upper(), entry.get("title", "").upper()}
        if raw_up in names:
            short = entry.get("shortName", entry["name"]).upper()
            return short, entry.get("type", "EVM")  # chainlist is EVM‑centric
    return "UNKNOWN", "UNKNOWN"

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def collect_platform_keys(raw_data: Dict[str, Any]) -> Set[str]:
    keys: Set[str] = set()
    for coin in raw_data.values():
        # 1) ERC‑style platforms mapping
        platforms = coin.get("platforms") or {}
        keys.update(platforms.keys())
        # 2) v3 field detail_platforms if present
        detail = coin.get("detail_platforms") or {}
        keys.update(detail.keys())
        # 3) asset_platform_id for native coins
        ap = coin.get("asset_platform_id")
        if ap:
            keys.add(ap)
    return {k for k in (_slug(k) for k in keys) if k}


def build_map(source: Path, dst: Path, force: bool = False) -> None:
    raw_data = _load_json(source)
    current: Dict[str, Dict[str, str]] = {} if force else _load_json(dst)

    discovered = collect_platform_keys(raw_data)
    missing = sorted(discovered - current.keys())
    if not missing:
        logger.info("network_map already up‑to‑date (%d entries)", len(current))
        return

    logger.info("%d new platform(s) detected", len(missing))
    chainlist = _fetch_chainlist()

    for platform in missing:
        code, typ = _match_chain(platform.replace("-", " "), chainlist)
        current[platform] = {"code": code, "type": typ}
        logger.info("added %-30s → {code:%s, type:%s}", platform, code, typ)

    _save_json(dict(sorted(current.items())), dst)
    logger.info("network_map written → %s (%d total)", dst, len(current))


def main() -> int:
    p = argparse.ArgumentParser(description="build or extend network_map.json")
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--map", type=Path, default=DEFAULT_MAP)
    p.add_argument("--force", action="store_true", help="ignore existing map")
    args = p.parse_args()

    if not args.source.exists():
        logger.error("%s not found – run fetch_raw_coin_data.py first", args.source)
        return 1

    build_map(args.source, args.map, force=args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
