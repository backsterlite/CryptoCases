import re
from typing import Dict, Any, List, Optional

from decimal import Decimal

from tronpy import Tron
from tronpy.keys import PrivateKey

from app.utils.signer import TronSigner
from app.services.blockchain.base import IBlockchainClient
from app.core.config.network_registry import NetworkRegistry
from app.core.config.settings import Settings

class TronClient(IBlockchainClient):
    
    ADDRESS_REGEX = re.compile(r"^T[a-zA-Z0-9]{33}$")

    
    def __init__(self, network_code: str, registry: NetworkRegistry):
        self.network_code = network_code
        self.registry = registry
        self.network_cfg = registry.get_network(network_code)
        
        # Initialize Tron client with RPC from registry
        rpc_url = self.network_cfg.rpc[0] if isinstance(self.network_cfg.rpc, list) else self.network_cfg.rpc
        self.client = Tron(provider_uri=rpc_url)
        self.signer = TronSigner()
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
        Prepare transaction for TRX or TRC20 token transfer
        """
        try:
            # Get token config from registry
            token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
            # Convert amount to atomic units
            atomic_amount = int(amount * Decimal(10 ** token_cfg.decimals))
            
            if token_cfg.contract:  # TRC20 Token transfer
                # Prepare TRC20 transfer
                unsigned = self.client.trx.trigger_smart_contract(
                    owner_address=from_address,
                    contract_address=token_cfg.contract,
                    function_selector="transfer(address,uint256)",
                    parameter=[
                        {"type": "address", "value": to_address},
                        {"type": "uint256", "value": atomic_amount}
                    ]
                )
            else:  # TRX transfer
                unsigned = self.client.trx.generate_transaction(
                    to=to_address,
                    amount=atomic_amount,
                    from_address=from_address
                )
            
            return unsigned
            
        except Exception as e:
            raise ValueError(f"Failed to prepare transaction: {str(e)}")

    def sign_transaction(self, unsigned_tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign the prepared transaction
        """
        try:
            return self.signer.sign_transaction(unsigned_tx)
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {str(e)}")

    def send_transaction(self, signed_tx: Dict[str, Any]) -> str:
        """
        Send signed transaction to the network
        """
        try:
            resp = self.client.trx.broadcast(signed_tx)
            return resp['txid']
        except Exception as e:
            raise ValueError(f"Failed to send transaction: {str(e)}")

    def get_confirmations(self, tx_hash: str) -> int:
        """
        Get number of confirmations for a transaction
        """
        try:
            info = self.client.trx.get_transaction_info(tx_hash)
            return info.get('receipt', {}).get('confirmations', 0)
        except Exception:
            return 0
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Tron address format and check if it exists on chain
        """
        try:
            # Check if address is valid format
            if not address.startswith('T'):
                return False
                
            # Try to decode address
            try:
                PrivateKey.from_base58check_address(address)
            except Exception:
                return False
                
            # Check if address exists on chain
            account = self.client.get_account(address)
            return account is not None
            
        except Exception:
            return False

    def get_balance(self, address: str, symbol: str, is_deposit: bool = True) -> Decimal:
        """
        Get balance of TRX or TRC20 token
        """
        try:
            # Get token config from registry
            token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
            if token_cfg.contract:  # TRC20 Token balance
                contract = self.client.get_contract(token_cfg.contract)
                balance = contract.functions.balanceOf(address)
                return Decimal(balance) / Decimal(10 ** token_cfg.decimals)
            else:  # TRX balance
                account = self.client.get_account(address)
                balance = account.get('balance', 0)
                return Decimal(balance) / Decimal(10 ** token_cfg.decimals)
                
        except Exception as e:
            raise ValueError(f"Failed to get balance: {str(e)}")

    def exists_on_chain(self, address: str) -> bool:
        """
        Check if address exists on chain
        """
        try:
            account = self.client.get_account(address)
            return account is not None
        except Exception:
            return False

    def close(self):
        """
        Close RPC connection
        """
        if hasattr(self.client, 'session'):
            self.client.session.close()

    def get_transactions(self, address: str, from_block: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all transactions for an address from a specific block
        """
        try:
            transactions = []
            
            # Get normal transactions
            if from_block is None:
                from_block = self.client.get_latest_block_number() - 1000  # Default to last 1000 blocks
                
            for block_number in range(from_block, self.client.get_latest_block_number() + 1):
                block = self.client.get_block(block_number)
                for tx in block['transactions']:
                    if tx['raw_data']['contract'][0]['type'] == 'TransferContract':
                        contract = tx['raw_data']['contract'][0]['parameter']['value']
                        if contract['owner_address'] == address or contract['to_address'] == address:
                            transactions.append({
                                'hash': tx['txID'],
                                'from': contract['owner_address'],
                                'to': contract['to_address'],
                                'value': Decimal(contract['amount']) / Decimal(10 ** 6),  # TRX has 6 decimals
                                'block_number': block_number,
                                'timestamp': block['block_header']['raw_data']['timestamp'],
                                'type': 'native'
                            })
            
            # Get TRC20 transfers
            for token in self.network_cfg.tokens:
                if token.contract:
                    contract = self.client.get_contract(token.contract)
                    events = contract.events.Transfer.get_logs(
                        from_block=from_block,
                        to_block=self.client.get_latest_block_number(),
                        filters={'to': address}
                    )
                    
                    for event in events:
                        transactions.append({
                            'hash': event['transaction_id'],
                            'from': event['result']['from'],
                            'to': event['result']['to'],
                            'value': Decimal(event['result']['value']) / Decimal(10 ** token.decimals),
                            'block_number': event['block_number'],
                            'timestamp': self.client.get_block(event['block_number'])['block_header']['raw_data']['timestamp'],
                            'type': 'trc20',
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
            return self.client.get_latest_block_number()
        except Exception as e:
            raise ValueError(f"Failed to get latest block: {str(e)}")

    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific transaction
        """
        try:
            tx = self.client.get_transaction(tx_hash)
            if not tx:
                raise ValueError("Transaction not found")
                
            contract = tx['raw_data']['contract'][0]
            if contract['type'] == 'TransferContract':
                value = contract['parameter']['value']
                return {
                    'hash': tx_hash,
                    'from': value['owner_address'],
                    'to': value['to_address'],
                    'value': Decimal(value['amount']) / Decimal(10 ** 6),
                    'block_number': tx['blockNumber'],
                    'timestamp': tx['block_timestamp'],
                    'status': tx['ret'][0]['contractRet']
                }
            else:
                raise ValueError("Unsupported transaction type")
                
        except Exception as e:
            raise ValueError(f"Failed to get transaction details: {str(e)}")

    def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
        """
        Check if transaction has required number of confirmations
        """
        try:
            tx = self.client.get_transaction(tx_hash)
            if not tx:
                return False
                
            current_block = self.client.get_latest_block_number()
            return (current_block - tx['blockNumber']) >= required_confirmations
        except Exception:
            return False
