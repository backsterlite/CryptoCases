from decimal import Decimal
from typing import Any, Dict, Optional, List
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_typing import Address
from eth_utils import to_checksum_address, is_address, to_normalized_address
from fastapi import Depends

from app.utils.signer import EvmSigner
from app.services.blockchain.base import IBlockchainClient
from app.core.config.settings import Settings
from app.api.deps import get_network_registry
from app.utils.hd_wallet import HDWalletService

class EVMClient(IBlockchainClient):
    
    def __init__(self, network_code: str, registry = Depends(get_network_registry)):
        self.network_code = network_code
        self.registry = registry
        self.network_cfg = registry.get_network(network_code)
        
        # Initialize Web3 with RPC from registry
        rpc_url = self.network_cfg.rpc[0] if isinstance(self.network_cfg.rpc, list) else self.network_cfg.rpc
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.signer = EvmSigner("")
        self.from_address = settings.PROJECT_WALLET_ADDRESS

    def prepare_transaction(
        self, 
        from_address: str, 
        to_address: str, 
        amount: Decimal,
        symbol: str,
        is_deposit: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare transaction for native token or ERC20 transfer
        """
        try:
            # Get token config from registry
            token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
            nonce = self.web3.eth.get_transaction_count(from_address)
            gas = kwargs.get('gas', settings.ETH_GAS_LIMIT)
            gas_price = self.web3.to_wei(kwargs.get('gas_price_gwei', settings.ETH_GAS_PRICE_GWEI), 'gwei')
            
            if token_cfg.contract:  # ERC20 Token transfer
                # Get token contract ABI and instance
                token_contract = self.web3.eth.contract(
                    address=to_checksum_address(token_cfg.contract),
                    abi=settings.ERC20_ABI
                )
                
                # Prepare transfer data
                atomic_amount = int(amount * Decimal(10 ** token_cfg.decimals))
                data = token_contract.encodeABI(
                    fn_name='transfer',
                    args=[to_address, atomic_amount]
                )
                
                tx = {
                    'nonce': nonce,
                    'to': token_cfg.contract,
                    'value': 0,
                    'gas': gas,
                    'gasPrice': gas_price,
                    'data': data,
                    'chainId': settings.ETH_CHAIN_ID
                }
            else:  # Native token transfer
                atomic_amount = int(amount * Decimal(10 ** token_cfg.decimals))
                tx = {
                    'nonce': nonce,
                    'to': to_address,
                    'value': atomic_amount,
                    'gas': gas,
                    'gasPrice': gas_price,
                    'chainId': settings.ETH_CHAIN_ID
                }
            
            return tx
            
        except Exception as e:
            raise ValueError(f"Failed to prepare transaction: {str(e)}")

    def sign_transaction(self, unsigned_tx: Dict[str, Any]) -> str:
        """
        Sign the prepared transaction
        """
        try:
            return self.signer.sign_transaction(unsigned_tx)
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {str(e)}")

    def send_transaction(self, signed_tx: str) -> str:
        """
        Send signed transaction to the network
        """
        try:
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx)
            return tx_hash.hex()
        except Exception as e:
            raise ValueError(f"Failed to send transaction: {str(e)}")

    def get_confirmations(self, tx_hash: str) -> int:
        """
        Get number of confirmations for a transaction
        """
        try:
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            if not receipt:
                return 0
            return receipt['confirmations'] if 'confirmations' in receipt else self.web3.eth.block_number - receipt.blockNumber
        except Exception:
            return 0

    def validate_address(self, address: str) -> bool:
        """
        Validate EVM address format and check if it exists on chain
        """
        try:
            # Check if address is valid format
            if not is_address(address):
                return False
                
            # Normalize address to checksum format
            checksum_address = to_checksum_address(address)
            
            # Verify checksum is valid
            if not self.web3.is_checksum_address(checksum_address):
                return False
                
            # Check if address is not zero address
            if checksum_address == "0x0000000000000000000000000000000000000000":
                return False
                
            # Check if address exists on chain by checking its code and balance
            code = self.web3.eth.get_code(checksum_address)
            balance = self.web3.eth.get_balance(checksum_address)
            
            # Address exists if it has code (is a contract) or has had any transactions (balance > 0)
            return len(code) > 0 or balance > 0
            
        except Exception:
            return False

    def get_balance(self, address: str, symbol: str, is_deposit: bool = True) -> Decimal:
        """
        Get balance of native token or ERC20 token
        """
        try:
            # Get token config from registry
            token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
            if token_cfg.contract:  # ERC20 Token balance
                token_contract = self.web3.eth.contract(
                    address=to_checksum_address(token_cfg.contract),
                    abi=settings.ERC20_ABI
                )
                balance = token_contract.functions.balanceOf(address).call()
                return Decimal(balance) / Decimal(10 ** token_cfg.decimals)
            else:  # Native token balance
                balance = self.web3.eth.get_balance(address)
                return Decimal(balance) / Decimal(10 ** token_cfg.decimals)
        except Exception as e:
            raise ValueError(f"Failed to get balance: {str(e)}")

    def exists_on_chain(self, address: str) -> bool:
        """
        Check if address exists on chain
        """
        try:
            code = self.web3.eth.get_code(address)
            return len(code) > 0
        except Exception:
            return False
        
    def close(self):
        """
        Close RPC connection
        """
        if hasattr(self.web3.provider, 'session'):
            self.web3.provider.session.close()

    def get_transactions(self, address: str, from_block: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all transactions for an address from a specific block
        """
        try:
            if from_block is None:
                from_block = self.web3.eth.block_number - 1000  # Default to last 1000 blocks

            # Get all transactions for the address
            transactions = []
            
            # Get normal transactions
            for block_number in range(from_block, self.web3.eth.block_number + 1):
                block = self.web3.eth.get_block(block_number, full_transactions=True)
                for tx in block.transactions:
                    if tx['from'].lower() == address.lower() or tx['to'] and tx['to'].lower() == address.lower():
                        transactions.append({
                            'hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': Decimal(tx['value']) / Decimal(10 ** 18),
                            'block_number': block_number,
                            'timestamp': block['timestamp'],
                            'type': 'native'
                        })

            # Get ERC20 transfers
            for token in self.network_cfg.tokens:
                if token.contract:
                    contract = self.web3.eth.contract(
                        address=token.contract,
                        abi=settings.ERC20_ABI
                    )
                    
                    transfer_filter = contract.events.Transfer.create_filter(
                        fromBlock=from_block,
                        argument_filters={'to': address}
                    )
                    
                    for event in transfer_filter.get_all_entries():
                        transactions.append({
                            'hash': event['transactionHash'].hex(),
                            'from': event['args']['from'],
                            'to': event['args']['to'],
                            'value': Decimal(event['args']['value']) / Decimal(10 ** token.decimals),
                            'block_number': event['blockNumber'],
                            'timestamp': self.web3.eth.get_block(event['blockNumber'])['timestamp'],
                            'type': 'erc20',
                            'token_address': token.contract
                        })

            return sorted(transactions, key=lambda x: x['block_number'])
            
        except Exception as e:
            raise ValueError(f"Failed to get transactions: {str(e)}")

    def get_latest_block(self) -> int:
        """
        Get the latest block number
        """
        try:
            return self.web3.eth.block_number
        except Exception as e:
            raise ValueError(f"Failed to get latest block: {str(e)}")

    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific transaction
        """
        try:
            tx = self.web3.eth.get_transaction(tx_hash)
            receipt = self.web3.eth.get_transaction_receipt(tx_hash)
            
            if not tx or not receipt:
                raise ValueError("Transaction not found")
                
            return {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': Decimal(tx['value']) / Decimal(10 ** 18),
                'block_number': tx['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': receipt['status'],
                'confirmations': self.get_confirmations(tx_hash)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get transaction details: {str(e)}")

    def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
        """
        Check if transaction has required number of confirmations
        """
        try:
            confirmations = self.get_confirmations(tx_hash)
            return confirmations >= required_confirmations
        except Exception:
            return False