# /home/backster/Backster_Work/Python/CryptoCases_Project/backend/src/app/utils/hd_wallet.py
"""
HD Wallet derivation utility for EVM, TRON, SOLANA, TON networks using BIP44.
"""
from typing import Tuple, Optional, List
from bip_utils import Bip44, Bip44Coins, Bip44Changes, Bip44ConfGetter
from tonutils.client import ToncenterV3Client
from tonutils.wallet.contract.v5 import WalletV5R1
from fastapi import Depends

from app.config.settings import settings
from app.db.models.hd_wallet_meta import HDWalletMeta
from app.services.blockchain.ton_client import TonClientWrapper
from app.api.deps import get_blockchain_factory

# Map our network types to BIP44 coins
NETWORK_COIN_MAP = {
    "EVM": Bip44Coins.ETHEREUM,   # Ethereum, Polygon, BSC, etc.
    "TRON": Bip44Coins.TRON,
    "SOLANA": Bip44Coins.SOLANA,
    # TON використовує окремий механізм
}

class HDWalletService:
    """
    Derives hierarchical deterministic addresses from a single master key.
    
    Supports two derivation methods:
    1. BIP44 standard for EVM/TRON/SOLANA networks
    2. TON-specific derivation using mnemonic + wallet_id
    """
    def __init__(self, mnemonic: str | List[str], xprv: str):
        # mnemonic: 12/24-word seed phrase
        self._mnemonic = mnemonic.split() if isinstance(mnemonic, str) else mnemonic
        # Extended private key for BIP44 chains
        self._xprv = xprv
        
    def derive_address(
        self,
        xpub: str,
        network: str,
        index: int
        ) -> Tuple[str | WalletV5R1, str | None]:
        """
        Universal address derivation method.
        Chooses appropriate derivation based on network type.

        :param network: One of 'EVM', 'TRON', 'SOLANA', 'TON'
        :param index: Derivation index (0-based)
        :return: Tuple(address, derivation_path)
        """
        network = network.upper()
        
        if network == "TON":
            return self.derive_ton_wallet(index)
        else:
            return self._derive_bip44_address(network, index, xpub)

    def _derive_bip44_address(
        self,
        network: str,
        index: int,
        xpub: str
        ) -> Tuple[str, str]:
        """
        Derive address using BIP44 standard for EVM/TRON/SOLANA networks.

        :param network: One of 'EVM', 'TRON', 'SOLANA'
        :param index: Derivation index (0-based)
        :return: Tuple(address, derivation_path)
        """
        try:
            coin = NETWORK_COIN_MAP[network]
            coin_conf = Bip44ConfGetter.GetConfig(coin)
        except KeyError:
            raise ValueError(f"Unsupported network for BIP44 derivation: {network}")

        # Initialize BIP44 from extended private key
        bip44_ctx = Bip44.FromExtendedKey(self._xprv, coin)
        
        derivation_template = settings.HD_DERIVATION_PATH_TEMPLATE
        
        # Derivation path: m/44'/coin'/0'/0/index
        addr_ctx = (bip44_ctx
            .Purpose()      # 44'
            .Coin()         # coin'
            .Account(0)     # account 0'
            .Change(Bip44Changes.CHAIN_EXT)  # 0 (external chain)
            .AddressIndex(index)  # index
        )
        
        address = addr_ctx.PublicKey().ToAddress()
        
        # Build the string path for logging
        path = derivation_template.format(coin_index=coin_conf.CoinIndex(), index=index)
        
        return address, path
        
    
    def derive_ton_wallet(
        self,
        factory=Depends(get_blockchain_factory),
        wallet_id: int = 0
        ) -> Tuple[WalletV5R1, None]:
        
        client: TonClientWrapper = factory.get_client("TON")
        wallet, priv, pub, _ = WalletV5R1.from_mnemonic(
            client=client.client,
            mnemonic=self._mnemonic,
            wallet_id=wallet_id
        )
        return wallet, None
    
 
    
    def validate_network(self, network: str) -> bool:
        """
        Validate if network is supported for derivation.
        
        :param network: Network name
        :return: True if supported
        """
        network = network.upper()
        return network in NETWORK_COIN_MAP or network == "TON"
    
    def get_supported_networks(self) -> list:
        """
        Get list of supported networks.
        
        :return: List of supported network names
        """
        return list(NETWORK_COIN_MAP.keys()) + ["TON"]