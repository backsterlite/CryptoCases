from decimal import Decimal

def send_evm_token(to_address: str, contract: str, amount: Decimal, decimals: int) -> str:
    # Stub implementation for sending EVM token
    print(f"[STUB:EVM] Sending {amount} tokens (decimals={decimals}) of contract {contract} to {to_address}")
    return "0xFAKE_EVM_TX_HASH"
