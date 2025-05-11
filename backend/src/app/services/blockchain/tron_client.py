from decimal import Decimal

def send_tron_token(to_address: str, contract: str, amount: Decimal, decimals: int) -> str:
    # Stub implementation for sending TRC20 token
    print(f"[STUB:TRON] Sending {amount} tokens (decimals={decimals}) of contract {contract} to {to_address}")
    return "FAKE_TRON_TX_ID"
