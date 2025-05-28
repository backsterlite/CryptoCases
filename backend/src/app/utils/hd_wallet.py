"""
HD Wallet derivation utility for EVM, TRON, SOLANA, TON networks using BIP44.
"""
from typing import Tuple
from bip_utils import Bip44, Bip44Coins, Bip44Changes
from app.config.settings import settings

# Map our network types to BIP44 coins
NETWORK_COIN_MAP = {
    "EVM": Bip44Coins.ETHEREUM,   # Ethereum, Polygon, BSC, etc.
    "TRON": Bip44Coins.TRON,
    "SOLANA": Bip44Coins.SOLANA,
    # "TON": Bip44Coins.TONCOIN, #TODO implement TON logic
}

class HDWalletService:
    """
    Derives hierarchical deterministic addresses from a single master key.

    Retrieves master extended private key from settings.HD_XPRV and derives
    network-specific addresses by index.
    """

    def __init__(self, xprv: str = settings.HD_XPRV):
        # Master extended private key (xprv) in BIP44 format
        self._xprv = xprv

    def derive_address(self, network: str, index: int) -> Tuple[str, str]:
        """
        Derive an address for the given network and index.

        :param network: One of 'EVM', 'TRON', 'SOLANA', 'TON'
        :param index: Derivation index (0-based)
        :return: Tuple(address, derivation_path)
        """
        network = network.upper()
        try:
            coin = NETWORK_COIN_MAP[network]
        except KeyError:
            raise ValueError(f"Unsupported network for HD derivation: {network}")

        # Initialize BIP44 from extended private key
        bip44_ctx = Bip44.FromExtendedKey(self._xprv, coin)
        # Derivation path: m/44'/coin'/0'/0/index
        addr_ctx = (bip44_ctx
            .Purpose()      # 44'
            .Coin()         # coin'
            .Account(0)     # account 0
            .Change(Bip44Changes.CHAIN_EXT)
            .AddressIndex(index)  # index
        )
        address = addr_ctx.PublicKey().ToAddress()
        # Build the string path for logging
        path = f"m/44'/{coin.CoinIndex()}'/0'/0/{index}"
        return address, path