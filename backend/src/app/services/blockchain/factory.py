from typing import Dict, Any
from app.config.network_registry import NetworkRegistry
from app.services.blockchain.evm_client import EVMClient
from app.services.blockchain.tron_client import TronClient
# from app.services.blockchain.ton_client import TonClientWrapper #TODO implement TON logic
from app.services.blockchain.solana_client import SolanaClient

class BlockchainClientFactory:
    def __init__(self, registry: NetworkRegistry):
        self.registry = registry
        self._clients: Dict[str, Any] = {}

    def get_client(self, network_code: str) -> Any:
        """
        Get blockchain client for network.
        Uses cached client if exists, creates new one otherwise.
        """
        if network_code not in self._clients:
            network_cfg = self.registry.get_network(network_code)
            self._clients[network_code] = self._create_client(network_code, network_cfg)
        return self._clients[network_code]

    def _create_client(self, network_code: str, network_cfg: Any) -> Any:
        """
        Create new blockchain client based on network type
        """
        network_type = network_cfg.type.upper()
        
        if network_type == "EVM":
            return EVMClient(network_code, self.registry)
        elif network_type == "TRON":
            return TronClient(network_code, self.registry)
        # elif network_type == "TON": #TODO implement TON logic
        #     return TonClientWrapper(network_code, self.registry)
        elif network_type == "SOLANA":
            return SolanaClient(network_code, self.registry)
        else:
            raise ValueError(f"Unsupported network type: {network_type}")

    def close_all(self):
        """
        Close all client connections
        """
        for client in self._clients.values():
            if hasattr(client, 'close'):
                client.close()
        self._clients.clear()
