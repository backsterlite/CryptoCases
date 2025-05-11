import json
import time
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).parent.parent

RAW_LIST_PATH = BASE_DIR / "data" / "raw_coin_list.json"
RAW_OUTPUT_PATH = BASE_DIR / "data" / "raw_coin_data.json"


COINGECKO_URL_TEMPLATE = "https://api.coingecko.com/api/v3/coins/"
COINGECKO_API_KEY = os.getenv("COINGECKO_API")

RATE_LIMIT_DELAY = 1.5  # seconds
COINGECKO_HEADERS = {
    "User-Agent": "PostmanRuntime/7.43.4",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "no-cache",
}

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": COINGECKO_API_KEY
}

headers = {**headers, **COINGECKO_HEADERS}
params = {
    "localization": "false",
    "tickers": "false",
    "market_data": "false",
    "community_data": "false",
    "sparkline": "false"
}

def fetch_coin_data(coin_id: str):
    url = f"{COINGECKO_URL_TEMPLATE}{coin_id}"
    r = requests.get(url, headers=headers, params=params)
    
    if r.status_code != 200:
        print(f"Failed to fetch {coin_id} — status {r.status_code}")
        return None
    return r.json()


def main():
    with open(RAW_LIST_PATH, "r") as f:
        coin_map = json.load(f)

    results = {}
    for internal_name, coingecko_id in coin_map.items():
        print(f"Fetching {internal_name} ({coingecko_id})...")
        data = fetch_coin_data(coingecko_id)
        if data:
            results[internal_name] = data
        time.sleep(RATE_LIMIT_DELAY)

    # with open(RAW_OUTPUT_PATH, "w") as f:
    #     json.dump(results, f, indent=2)

    print(f"Saved {len(results)} entries to {RAW_OUTPUT_PATH}")


if __name__ == "__main__":
    main()