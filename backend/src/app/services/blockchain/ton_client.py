# # src/app/services/blockchain/tonutils_client.py #TODO implement TON logic
# from decimal import Decimal
# from typing import Any, Dict, List, Optional

# from tonutils import TonClient
# from tonutils.contracts.tip3_token import Tip3Token
# from tonutils.crypto import KeyPair, keypair_from_secret, sign_boc

# from app.services.blockchain.base import IBlockchainClient
# from app.config.network_registry import NetworkRegistry


# class TonClientWrapper(IBlockchainClient):
#     """
#     Wrapper around tonutils for native TON and TIP-3 (Jetton) transfers.
#     """

#     def __init__(self, network_code: str, registry: NetworkRegistry):
#         self.network_code = network_code
#         self.registry = registry
#         net_cfg = registry.get_network(network_code)
#         # Підтримуємо списки RPC або один рядок
#         rpc = net_cfg.rpc if isinstance(net_cfg.rpc, list) else [net_cfg.rpc]
#         self.client = TonClient(rpc_endpoints=rpc)
#         # Ключ для підпису (секретний ключ у hex чи base64)
#         self._keypair: KeyPair = keypair_from_secret(registry.get_network(network_code).vault_key_id)

#         # Власна адреса проекту
#         self.from_address = registry.get_network(network_code).from_address

#     def prepare_transaction(
#         self,
#         from_address: str,
#         to_address: str,
#         amount: Decimal,
#         symbol: str,
#         is_deposit: bool = True,
#         **kwargs,
#     ) -> bytes:
#         token_cfg = self.registry.token_cfg(
#             self.network_code, symbol, "deposit" if is_deposit else "withdrawal"
#         )
#         atomic = int(amount * (10 ** token_cfg.decimals))

#         # Якщо це Jetton (TIP-3)
#         if token_cfg.contract:
#             tip3 = Tip3Token(token_cfg.contract, self.client)
#             unsigned_boc = tip3.build_transfer_msg(
#                 self._keypair,
#                 to_address,
#                 atomic,
#                 bounce=False,
#                 # додаткові payload, якщо треба
#             )
#         else:
#             # Native TON transfer
#             unsigned_boc = self.client.boc.create_transfer_message(
#                 from_address=from_address,
#                 to_address=to_address,
#                 amount=atomic,
#                 bounce=False,
#             )
#         return unsigned_boc

#     def sign_transaction(self, unsigned_boc: bytes) -> bytes:
#         # Підписуємо BOC і повертаємо signed BOC
#         return sign_boc(unsigned_boc, self._keypair)

#     def send_transaction(self, signed_boc: bytes) -> str:
#         tx = self.client.send_message(signed_boc)
#         return tx.id

#     def validate_address(self, address: str) -> bool:
#         # Перевірка формату та існування
#         try:
#             # Address.check_improper формально перевіряє формат
#             if not TonClient.address.is_valid(address):
#                 return False
#             # Існування на ланцюгу
#             acc = self.client.net.get_account(address)
#             return acc.status != "uninit"
#         except Exception:
#             return False

#     def exists_on_chain(self, address: str) -> bool:
#         return self.validate_address(address)

#     def get_balance(self, address: str, symbol: str, is_deposit: bool = True) -> Decimal:
#         token_cfg = self.registry.token_cfg(
#             self.network_code, symbol, "deposit" if is_deposit else "withdrawal"
#         )
#         if token_cfg.contract:
#             tip3 = Tip3Token(token_cfg.contract, self.client)
#             bal = tip3.get_balance(address)
#         else:
#             bal = self.client.net.get_account(address).balance
#         return Decimal(bal) / (10 ** token_cfg.decimals)

#     def get_transactions(
#         self, address: str, from_block: Optional[int] = None
#     ) -> List[Dict[str, Any]]:
#         # За прикладом RPC: використовуємо net.get_transactions або query_collection
#         raw = self.client.net.get_transactions(address, limit=50)
#         txs = []
#         for r in raw:
#             value = int(r.in_msg.value or 0) if r.in_msg else 0
#             txs.append({
#                 "hash": r.id,
#                 "from": r.in_msg.src if r.in_msg else None,
#                 "to": address,
#                 "value": Decimal(value) / (10 ** 9),
#                 "block_number": r.block_id,
#                 "timestamp": r.now,
#                 "type": "native"
#             })
#             # Аналогічно для out_msgs...
#         return txs

#     def get_latest_block(self) -> int:
#         head = self.client.net.get_masterchain_info()
#         return head.last.seqno

#     def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
#         info = self.client.net.get_transaction(tx_hash)
#         return {
#             "hash": info.id,
#             "from": info.in_msg.src if info.in_msg else None,
#             "to": info.in_msg.dst if info.in_msg else None,
#             "value": Decimal(info.in_msg.value or 0) / (10 ** 9),
#             "block_number": info.utime,
#             "status": info.status,
#             "timestamp": info.now
#         }

#     def is_transaction_confirmed(self, tx_hash: str, required_confirmations: int = 1) -> bool:
#         # Для TON вважаємо «підтвердженим», якщо воно з’явилось у ланцюгу
#         try:
#             return bool(self.get_transaction_details(tx_hash))
#         except Exception:
#             return False

#     def close(self):
#         # Наприклад, закриваємо HTTP-сесію, якщо потрібно
#         if hasattr(self.client, "session"):
#             self.client.session.close()
