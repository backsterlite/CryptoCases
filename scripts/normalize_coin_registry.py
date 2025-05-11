import json
from pathlib import Path
from typing import Dict, Optional, Any

BASE_DIR = Path(__file__).parent.parent
RAW_PATH =  BASE_DIR / "data" /"raw_coin_data.json"
NETWORK_MAP_PATH = BASE_DIR / "data" / "network_map.json"
OUTPUT_PATH = BASE_DIR / "data" / "coin_registry.json"

DEFAULT_DECIMALS = 18


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def get_first_network(platforms: Dict[str,str]) -> Optional[str]:
    for key in platforms.keys():
        if platforms[key]:
            return key
    return None

def normalize(raw_data, network_map) -> Dict[str,Any]:
    registry = {}

    for coin_id, data in raw_data.items():
        coingecko_id = data.get("id")
        symbol = data.get("symbol")
        name = data.get("name")
        thumb = data.get("image", {}).get("thumb")

        platforms = data.get("platforms", {})
        details = data.get("detail_platforms", {})

        contract_addresses = {}
        decimals = {}

        for net_raw, contract in platforms.items():
            net_std = network_map.get(net_raw.upper())
            if not net_std:
                continue
            net_code = net_std["code"]
            net_type = net_std["type"]

            contract_addresses[net_code] = {
                "raw": net_raw.upper(),
                "contract": contract,
                "type": net_type
            }

            detail = details.get(net_raw)
            if detail and detail.get("decimal_place") is not None:
                decimals[net_code] = {
                    "raw": net_raw.upper(),
                    "decimal_place": detail["decimal_place"] or DEFAULT_DECIMALS
                }

        is_token = bool(contract_addresses)

        if is_token:
            native_network = None
        elif data.get("asset_platform_id"):
            native_network = data.get("asset_platform_id").upper()
        elif get_first_network(platforms=platforms):
            native_network = get_first_network(platforms=platforms).upper()
        else:
            native_network = name.upper()

        registry[coin_id.upper()] = {
            "coin_symbol": symbol,
            "coin_name": name,
            "coin_thumb": thumb,
            "coin_contract_addresses": contract_addresses,
            "coin_decimals": decimals,
            "coingecko_id": coingecko_id,
            "is_native": not is_token,
            "native_network": native_network
        }

    return registry

def main():
    raw = load_json(RAW_PATH)
    network_map = load_json(NETWORK_MAP_PATH)
    result = normalize(raw, network_map)

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Normalized {len(result)} tokens to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()