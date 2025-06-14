# src/app/services/blockchain/tonutils_client.py #TODO implement TON logic
from decimal import Decimal
from typing import Any, Dict, List, Optional

from tonutils.client import ToncenterV3Client
from tonutils.wallet.contract.v4 import WalletV4R2
from tonutils.jetton import JettonWalletStablecoin, JettonMasterStablecoin

from app.services.blockchain.base import IBlockchainClient
from app.config.network_registry import NetworkRegistry


class TonClientWrapper(IBlockchainClient):
    """
    Wrapper around tonutils for native TON and TIP-3 (Jetton) transfers.
    """

    def __init__(self, network_code: str, registry: NetworkRegistry):
       self._client = ToncenterV3Client(rps=1)

    async def deploy_wallet(self, wallet: WalletV4R2) -> str:
        """
        Розгорнути контракт гаманця та повернути tx_hash.
        """
        result = await wallet.deploy()
        return result 
    
    async def send_native(
        self,
        from_wallet: WalletV4R2,
        to_address: str,
        amount: Decimal
    ) -> str:
        """
        Перекласти native TON.
        """
        tx = await from_wallet.transfer(to_address, amount)
        return tx

    async def send_jetton(
        self,
        from_wallet: WalletV4R2,
        jetton_contract: str,
        to_address: str,
        amount: Decimal
    ) -> str:
        """
        Перекласти TIP-3 jetton (USDT, USDC).
        """
        JettonWalletStablecoin.
        tx = await from_wallet.transfer_jetton(
            jetton_contract=jetton_contract,
            to_address=to_address,
            amount=amount
        )
        return tx

    def prepare_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: Decimal,
        symbol: str,
        is_deposit: bool = True,
        **kwargs,
    ) -> bytes:
        pass

    def sign_transaction(self, unsigned_boc: bytes) -> bytes:
        pass

    def send_transaction(self, signed_boc: bytes) -> str:
       pass

    def validate_address(self, address: str) -> bool:
       pass
    def get_transactions(
        self, address: str, from_block: Optional[int] = None
    ) -> List[Dict[str, Any]]:
       pass

    def get_latest_block(self) -> int:
        head = self.client.net.get_masterchain_info()
        return head.last.seqno

    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        pass

    def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
        pass

    def close(self):
        pass
    
    @property
    def client(self) -> ToncenterV3Client:
        return self._client
