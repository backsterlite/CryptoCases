from decimal import Decimal
from typing import Any, Dict, Optional, Tuple, List
from solana.rpc.api import Client as SolanaClient
from solana.rpc.commitment import Commitment
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from spl.token.client import Token as SplToken
from spl.token.constants import TOKEN_PROGRAM_ID

from app.services.blockchain.base import IBlockchainClient
from app.config.network_registry import NetworkRegistry
from app.config.settings import settings
from app.utils.hd_wallet import HDWalletService

class SOLClient(IBlockchainClient):
    def __init__(self, network_code: str, registry: NetworkRegistry):
        self.network_code = network_code
        self.registry = registry
        self.network_cfg = registry.get_network(network_code)
        
        # Initialize Solana client with RPC from registry
        rpc_url = self.network_cfg.rpc[0] if isinstance(self.network_cfg.rpc, list) else self.network_cfg.rpc
        self.client = SolanaClient(rpc_url, commitment=Commitment("confirmed"))
        self.from_address = settings.PROJECT_WALLET_ADDRESS

    # def prepare_transaction(
    #     self, 
    #     from_address: str, 
    #     to_address: str, 
    #     amount: Decimal,
    #     symbol: str,
    #     is_deposit: bool = True,
    #     **kwargs
    # ) -> Dict[str, Any]:
    #     """
    #     Prepare transaction for SOL or SPL token transfer
    #     """
    #     try:
    #         # Get token config from registry
    #         token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
    #         # Convert amount to atomic units
    #         atomic_amount = int(amount * Decimal(10 ** token_cfg.decimals))
            
    #         if token_cfg.contract:  # SPL Token transfer
    #             # Get token contract
    #             token = SplToken(
    #                 self.client,
    #                 PublicKey(token_cfg.contract),
    #                 TOKEN_PROGRAM_ID,
    #                 Keypair.from_secret_key(bytes.fromhex(settings.PROJECT_WALLET_PRIVATE_KEY))
    #             )
                
    #             # Get associated token accounts
    #             from_ata = token.get_accounts_by_owner(PublicKey(from_address))[0]
    #             to_ata = token.get_accounts_by_owner(PublicKey(to_address))[0]
                
    #             # Prepare transfer instruction
    #             transfer_ix = token.transfer(
    #                 source=from_ata.pubkey,
    #                 dest=to_ata.pubkey,
    #                 owner=PublicKey(from_address),
    #                 amount=atomic_amount
    #             )
                
    #             return {
    #                 'instructions': [transfer_ix],
    #                 'signers': [],
    #                 'fee_payer': PublicKey(from_address)
    #             }
    #         else:  # SOL transfer
    #             # Prepare transfer instruction
    #             transfer_ix = self.client.transfer(
    #                 from_pubkey=PublicKey(from_address),
    #                 to_pubkey=PublicKey(to_address),
    #                 lamports=atomic_amount
    #             )
                
    #             return {
    #                 'instructions': [transfer_ix],
    #                 'signers': [],
    #                 'fee_payer': PublicKey(from_address)
    #             }
            
    #     except Exception as e:
    #         raise ValueError(f"Failed to prepare transaction: {str(e)}")

    def sign_transaction(self, unsigned_tx: Dict[str, Any]) -> str:
        """
        Sign the prepared transaction
        """
        try:
            transaction = Transaction()
            transaction.add(*unsigned_tx['instructions'])
            transaction.fee_payer = unsigned_tx['fee_payer']
            
            # Sign transaction
            signed_tx = transaction.sign(*unsigned_tx['signers'])
            return signed_tx.serialize().hex()
            
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {str(e)}")

    def send_transaction(self, signed_tx: str) -> str:
        """
        Send signed transaction to the network
        """
        try:
            result = self.client.send_raw_transaction(bytes.fromhex(signed_tx))
            return result['result']
        except Exception as e:
            raise ValueError(f"Failed to send transaction: {str(e)}")

    def get_confirmations(self, tx_hash: str) -> int:
        """
        Get number of confirmations for a transaction
        """
        try:
            status = self.client.get_signature_statuses([tx_hash])
            if not status['result']['value'][0]:
                return 0
            return status['result']['value'][0]['confirmations'] or 0
        except Exception:
            return 0

    # def validate_address(self, address: str) -> bool:
    #     """
    #     Validate Solana address format and check if it exists on chain
    #     """
    #     try:
    #         # Check if address is valid format
    #         pubkey = PublicKey(address)
            
    #         # Check if address is not zero address
    #         if pubkey.to_base58() == "11111111111111111111111111111111":
    #             return False
                
    #         # Check if address exists on chain by checking its balance
    #         balance = self.client.get_balance(pubkey)
            
    #         # For SPL tokens, check if account exists
    #         if self.network_cfg.tokens:  # If network supports tokens
    #             for token in self.network_cfg.tokens:
    #                 if token.contract:  # If token is SPL
    #                     token_accounts = self.client.get_token_accounts_by_owner(
    #                         pubkey,
    #                         {'mint': PublicKey(token.contract)}
    #                     )
    #                     if token_accounts['result']['value']:
    #                         return True
            
    #         # Address exists if it has any SOL balance
    #         return balance['result']['value'] > 0
            
    #     except Exception:
    #         return False

    # def get_balance(self, address: str, symbol: str, is_deposit: bool = True) -> Decimal:
    #     """
    #     Get balance of SOL or SPL token
    #     """
    #     try:
    #         # Get token config from registry
    #         token_cfg = self.registry.token_cfg(self.network_code, symbol, "deposit" if is_deposit else "withdrawal")
            
    #         pubkey = PublicKey(address)
            
    #         if token_cfg.contract:  # SPL Token balance
    #             token = SplToken(
    #                 self.client,
    #                 PublicKey(token_cfg.contract),
    #                 TOKEN_PROGRAM_ID,
    #                 Keypair.from_secret_key(bytes.fromhex(settings.PROJECT_WALLET_PRIVATE_KEY))
    #             )
                
    #             accounts = token.get_accounts_by_owner(pubkey)
    #             if not accounts:
    #                 return Decimal(0)
                    
    #             balance = accounts[0].amount
    #             return Decimal(balance) / Decimal(10 ** token_cfg.decimals)
    #         else:  # SOL balance
    #             balance = self.client.get_balance(pubkey)
    #             return Decimal(balance['result']['value']) / Decimal(10 ** token_cfg.decimals)
                
    #     except Exception as e:
    #         raise ValueError(f"Failed to get balance: {str(e)}")

    # def exists_on_chain(self, address: str) -> bool:
    #     """
    #     Check if address exists on chain
    #     """
    #     try:
    #         pubkey = PublicKey(address)
    #         balance = self.client.get_balance(pubkey)
    #         return balance['result']['value'] > 0
    #     except Exception:
    #         return False

    # def close(self):
    #     """
    #     Close RPC connection
    #     """
    #     if hasattr(self.client, 'session'):
    #         self.client.session.close()

    # def get_transactions(self, address: str, from_block: Optional[int] = None) -> List[Dict[str, Any]]:
    #     """
    #     Get all transactions for an address from a specific block
    #     """
    #     try:
    #         transactions = []
    #         pubkey = PublicKey(address)
            
    #         # Get SOL transfers
    #         signatures = self.client.get_signatures_for_address(pubkey)
    #         for sig_info in signatures:
    #             if from_block and sig_info['slot'] < from_block:
    #                 continue
                    
    #             tx = self.client.get_transaction(sig_info['signature'])
    #             if not tx:
    #                 continue
                    
    #             # Process SOL transfers
    #             for instruction in tx['transaction']['message']['instructions']:
    #                 if instruction['programId'] == 'system' and instruction['data'].startswith('2'):  # Transfer instruction
    #                     transactions.append({
    #                         'hash': sig_info['signature'],
    #                         'from': instruction['accounts'][0],
    #                         'to': instruction['accounts'][1],
    #                         'value': Decimal(instruction['data'][2:]) / Decimal(10 ** 9),  # SOL has 9 decimals
    #                         'block_number': sig_info['slot'],
    #                         'timestamp': sig_info['blockTime'],
    #                         'type': 'native'
    #                     })
            
    #         # Get SPL token transfers
    #         for token in self.network_cfg.tokens:
    #             if token.contract:
    #                 token_pubkey = PublicKey(token.contract)
    #                 token_accounts = self.client.get_token_accounts_by_owner(
    #                     pubkey,
    #                     {'mint': token_pubkey}
    #                 )
                    
    #                 for account in token_accounts['result']['value']:
    #                     account_pubkey = PublicKey(account['pubkey'])
    #                     signatures = self.client.get_signatures_for_address(account_pubkey)
                        
    #                     for sig_info in signatures:
    #                         if from_block and sig_info['slot'] < from_block:
    #                             continue
                                
    #                         tx = self.client.get_transaction(sig_info['signature'])
    #                         if not tx:
    #                             continue
                                
    #                         # Process SPL transfers
    #                         for instruction in tx['transaction']['message']['instructions']:
    #                             if instruction['programId'] == TOKEN_PROGRAM_ID:
    #                                 transactions.append({
    #                                     'hash': sig_info['signature'],
    #                                     'from': instruction['accounts'][1],
    #                                     'to': instruction['accounts'][2],
    #                                     'value': Decimal(instruction['data'][2:]) / Decimal(10 ** token.decimals),
    #                                     'block_number': sig_info['slot'],
    #                                     'timestamp': sig_info['blockTime'],
    #                                     'type': 'spl',
    #                                     'token_address': token.contract
    #                                 })
            
    #         return sorted(transactions, key=lambda x: x['block_number'])
            
    #     except Exception as e:
    #         raise ValueError(f"Failed to get transactions: {str(e)}")

    def get_latest_block(self) -> int:
        """
        Get the latest block number (slot)
        """
        try:
            return self.client.get_slot()
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
                
            return {
                'hash': tx_hash,
                'block_number': tx['slot'],
                'timestamp': tx['blockTime'],
                'status': 'success' if tx['meta']['err'] is None else 'failed',
                'fee': Decimal(tx['meta']['fee']) / Decimal(10 ** 9)
            }
            
        except Exception as e:
            raise ValueError(f"Failed to get transaction details: {str(e)}")

    def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
        """
        Check if transaction has required number of confirmations
        For Solana, we consider a transaction confirmed if it's in a block
        """
        try:
            tx = self.client.get_transaction(tx_hash)
            return tx is not None
        except Exception:
            return False
