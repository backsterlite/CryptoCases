from typing import Dict, Any


def check_is_native_token(data: Dict[str,Any]) -> bool:
    local_data = data.copy()
    platforms = local_data.get("platforms", {})
    contract_platforms = {k: v for k, v in platforms.items() if v}
    return not bool(contract_platforms)