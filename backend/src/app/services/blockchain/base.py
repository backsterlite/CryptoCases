from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional

class IBlockchainClient(ABC):
    @abstractmethod
    def prepare_transaction(self, from_address: str, to_address: str, amount: Decimal, **kwargs) -> Dict[str, Any]:
        """
        Prepare unsigned transaction data
        """
        pass

    @abstractmethod
    def sign_transaction(self, unsigned_tx: Dict[str, Any]) -> Any:
        """
        Sign an unsigned transaction and return signed_tx
        """
        pass

    @abstractmethod
    def send_transaction(self, signed_tx: Any) -> str:
        """
        Sends signed transaction on-chain, returns tx_hash
        """
        pass

    @abstractmethod
    def get_confirmations(self, tx_hash: str) -> int:
        """
        Gets the number of transaction confirmations
        """
        pass
    
    @abstractmethod
    def validate_address(self, address: str) -> bool:
        """
        Validate that the given address is correctly formatted for this blockchain.
        Returns True if valid, False otherwise.
        """
        pass

    @abstractmethod
    def get_balance(self, address: str, symbol: str, is_deposit: bool = True) -> Decimal:
        """
        Get balance of native token or token contract
        """
        pass

    @abstractmethod
    def get_transactions(self, address: str, from_block: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all transactions for an address from a specific block
        Returns list of transactions with their details
        """
        pass

    @abstractmethod
    def get_latest_block(self) -> int:
        """
        Get the latest block number
        """
        pass

    @abstractmethod
    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific transaction
        """
        pass

    @abstractmethod
    def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
        """
        Check if transaction has required number of confirmations
        """
        pass