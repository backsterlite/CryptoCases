# import json
# import time
# import os
# import requests
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()
# BASE_DIR = Path(__file__).parent.parent

# RAW_LIST_PATH = BASE_DIR / "data" / "raw_coin_list.json"
# RAW_OUTPUT_PATH = BASE_DIR / "data" / "raw_coin_data.json"


# COINGECKO_URL_TEMPLATE = "https://api.coingecko.com/api/v3/coins/"
# COINGECKO_API_KEY = "CG-emDJCDWmXRDeo5B5pAbxYFZT"

# RATE_LIMIT_DELAY = 1.5  # seconds
# COINGECKO_HEADERS = {
#     "User-Agent": "PostmanRuntime/7.43.4",
#     "Accept": "*/*",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Connection": "keep-alive",
#     "Cache-Control": "no-cache",
# }

# headers = {
#     "accept": "application/json",
#     "x-cg-demo-api-key": COINGECKO_API_KEY
# }

# headers = {**headers, **COINGECKO_HEADERS}
# params = {
#     "localization": "false",
#     "tickers": "false",
#     "market_data": "false",
#     "community_data": "false",
#     "sparkline": "false"
# }

# def fetch_coin_data(coin_id: str):
#     url = f"{COINGECKO_URL_TEMPLATE}{coin_id}"
#     r = requests.get(url, headers=headers, params=params)
    
#     if r.status_code != 200:
#         print(f"Failed to fetch {coin_id} — status {r.status_code}")
#         return None
#     return r.json()


# def main():
#     with open(RAW_LIST_PATH, "r") as f:
#         coin_map = json.load(f)

#     results = {}
#     for internal_name, coingecko_id in coin_map.items():
#         print(f"Fetching {internal_name} ({coingecko_id})...")
#         data = fetch_coin_data(coingecko_id)
#         if data:
#             results[coingecko_id] = data
#         time.sleep(RATE_LIMIT_DELAY)

#     with open(RAW_OUTPUT_PATH, "w") as f:
#         json.dump(results, f, indent=2)

#     print(f"Saved {len(results)} entries to {RAW_OUTPUT_PATH}")


# if __name__ == "__main__":
#     main()
    
#!/usr/bin/env python3
"""
fetch_raw_coin_data.py
======================
Pull raw payloads from Coingecko for every coin defined in
`data/raw_coin_list.json` and write the aggregated blob to
`data/raw_coin_data.json`.

Highlights
----------
* **Keeps original layout** (BASE_DIR logic, same input/output paths).
* Adds CLI flags: `--delay`, `--list`, `--output`, `--append`, `--quiet`.
* Respects free‑tier rate‑limit and retries transient errors.
* Deterministic ordering → minimal git‑diffs.
* When `--append` is set, merges into existing JSON instead of clobbering.

Run:
```bash
python scripts/fetch_raw_coin_data.py --delay 1.8 --append
```
Exit codes: 0 = success, 2 = some coins failed.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# paths & env
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LIST = BASE_DIR / "data" / "raw_coin_list.json"
DEFAULT_OUTPUT = BASE_DIR / "data" / "raw_coin_data.json"

load_dotenv()

COINGECKO_BASE_URL = os.getenv(
    "COINGECKO_BASE_URL",
    "https://api.coingecko.com/api/v3/coins/",
)
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "CG-emDJCDWmXRDeo5B5pAbxYFZT")

REQ_HEADERS = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY,
    "User-Agent": "CryptoCases/1.0 (+github.com/cryptocases)",
}

REQ_PARAMS = {
    "localization": "false",
    "tickers": "false",
    "market_data": "false",
    "community_data": "false",
    "developer_data": "true",
    "sparkline": "false",
}

# ---------------------------------------------------------------------------
# logging & HTTP session
# ---------------------------------------------------------------------------

logger = logging.getLogger("fetch_raw_coin_data")
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO
)

session = requests.Session()

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _clear_trash(data: dict) -> dict:
    """
    Фільтрує вхідний JSON-об'єкт, залишаючи тільки зазначені ключі.

    Args:
        data (dict): Вхідний JSON-об’єкт з усім набором полів.

    Returns:
        dict: Новий об’єкт, що містить лише ключі:
              asset_platform_id,
              symbol,
              web_slug,
              platforms,
              name,
              id,
              hashing_algorithm,
              image,
              contract_address,
              detail_platforms.
    """
    # Список ключів, які хочемо залишити
    keys_to_keep = [
        "asset_platform_id",
        "symbol",
        "web_slug",
        "platforms",
        "name",
        "id",
        "hashing_algorithm",
        "image",
        "contract_address",
        "detail_platforms"
    ]

    # Формуємо новий словник із зазначеними ключами, якщо вони є у вхідних даних
    filtered = {key: data.get(key) for key in keys_to_keep}
    return filtered

def _get(url: str, retry: int = 3) -> Dict[str, Any]:
    """GET URL with simple retry/back‑off, return empty dict on failure."""
    backoff = 1.0
    for attempt in range(1, retry + 1):
        try:
            r = session.get(url, headers=REQ_HEADERS, params=REQ_PARAMS, timeout=20)
            if r.status_code == 200:
                return r.json()
            logger.warning("%s – HTTP %s", url, r.status_code)
        except requests.RequestException as exc:  # network or timeout
            logger.warning("%s – %s", url, exc)
        if attempt < retry:
            time.sleep(backoff)
            backoff *= 2
    return {}


def fetch(coin_id: str) -> Dict[str, Any]:
    return _get(f"{COINGECKO_BASE_URL}{coin_id}")


# ---------------------------------------------------------------------------
# json utils
# ---------------------------------------------------------------------------

def load_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else {}


def save_json(obj: Any, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    tmp.replace(path)

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="Fetch raw Coingecko payloads")
    p.add_argument("--delay", type=float, default=1.5, help="sleep between API calls (s)")
    p.add_argument("--list", type=Path, default=DEFAULT_LIST, help="path to raw_coin_list.json")
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="output file path")
    p.add_argument("--append", action="store_true", help="merge into existing output")
    p.add_argument("--quiet", action="store_true", help="log only warnings/errors")
    args = p.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARNING)

    try:
        coin_map: Dict[str, str] = load_json(args.list)
    except Exception as exc:  # noqa: BLE001
        logger.error("cannot read %s – %s", args.list, exc)
        return 1

    existing = load_json(args.output) if args.append else {}
    result: Dict[str, Any] = existing.copy()
    failed: List[str] = []

    for internal_id, gecko_id in sorted(coin_map.items(), key=lambda kv: kv[0]):
        if internal_id in result:
            logger.info("skip %-20s (cached)", internal_id)
            continue
        logger.info("fetch %-20s <- %s", internal_id, gecko_id)
        data = fetch(gecko_id)
        if not data:
            failed.append(internal_id)
            continue
        data = _clear_trash(data)
        result[internal_id] = data
        time.sleep(args.delay)

    save_json(result, args.output)
    logger.info("saved %d coins → %s", len(result), args.output)

    if failed:
        logger.error("%d coin(s) failed", len(failed))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
