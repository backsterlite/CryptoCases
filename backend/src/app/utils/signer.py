"""
Signer abstractions for blockchain transactions across networks.
"""
from abc import ABC, abstractmethod
from typing import Any

from tronpy.keys import PrivateKey as TronPrivateKey
from web3 import Web3
from solders.keypair import Keypair
from solders.transaction import Transaction


# from tonutils import Address 
# from tonutils.crypto import keypair_from_secret, sign_boc
# from tonutils.client import TonClient

from app.core.config.settings import Settings
from app.core.config.settings import get_settings


settings: Settings = get_settings() 
class Signer(ABC):
    """Abstract Signer interface"""

    @abstractmethod
    def sign_transaction(self, tx: Any) -> Any:
        """Sign a prepared transaction object and return the signed transaction."""
        pass

# EVM signer

class EvmSigner(Signer):
    def __init__(self, private_key: str):
        self._web3 = Web3()
        self._account = self._web3.eth.account.from_key(private_key)

    def sign_transaction(self, tx: dict) -> dict:
        # Expects a dict with fields: nonce, gasPrice, gas, to, value, data, chainId
        signed = self._account.sign_transaction(tx)
        return signed.rawTransaction

# Tron signer

class TronSigner(Signer):
    def __init__(self, private_key_hex: str):
        # private_key_hex without 0x prefix
        self._pk = TronPrivateKey(bytes.fromhex(private_key_hex))

    def sign_transaction(self, tx: Any) -> Any:
        # Expects tx is a TronPY TransactionBuilder
        return tx.sign(self._pk)

# Solana signer

class SolanaSigner(Signer):
    def __init__(self, secret_key: bytes):
        # secret_key is a 64-byte secret key
        self._keypair = Keypair.from_secret_key(secret_key)

    def sign_transaction(self, tx: Transaction) -> Any:
        # tx is a solana.transaction.Transaction
        tx.sign(self._keypair)
        return tx

# TON signer #TODO implement TON logic
 # For address format, using tonutils
# class TonSigner:
#     """Signer for TON TIP-3 transactions using tonutils."""
#     def __init__(self, private_key_hex: str = settings.TON_PRIVATE_KEY, rpc_endpoints=None):
#         # private_key_hex is hex string or base64 secret key
#         # Initialize KeyPair for signing
#         self._keypair = keypair_from_secret(private_key_hex)
#         # Initialize client for existence check or send
#         self._client = TonClient(rpc_endpoints=rpc_endpoints)

#     def sign_transaction(self, unsigned_boc: bytes) -> bytes:
#         """
#         Sign a BOC (Bag of Cells) unsigned message
#         and return the signed BOC ready for send_message.
#         """
#         return sign_boc(unsigned_boc, self._keypair)

# Factory
def get_signer(network: str) -> Signer:
    network = network.upper()
    if network == "EVM":
        return EvmSigner("")
    if network == "TRON":
        return TronSigner("")
    if network == "SOLANA":
        return SolanaSigner(b"")
    # if network == "TON":
    #     return TonSigner()
    raise ValueError(f"Unsupported network for signing: {network}")
