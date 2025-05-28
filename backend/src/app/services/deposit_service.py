import qrcode
import base64
from io import BytesIO
from decimal import Decimal
from datetime import datetime, timezone
from typing import Optional, Dict

from fastapi import Depends, HTTPException, status

from app.api.deps import get_network_registry, get_external_wallet_service
from app.config.network_registry import NetworkRegistry, UnknownNetworkError, UnsupportedTokenError
from app.db.models.external_wallet import ExternalWallet
from app.db.models.deposit_log import DepositLog
from app.services.internal_balance_service import InternalBalanceService
from app.services.external_wallet_service import ExternalWalletService

class DepositService:
    """
    Service for handling on-chain deposits and adjusting internal user balances.
    Validates network and token, records deposit logs, and updates internal balance.
    """
    def __init__(
        self,
        registry: NetworkRegistry = Depends(get_network_registry),
        external_wallet_service: ExternalWalletService = Depends(get_external_wallet_service)
    ):
        self.registry = registry
        self.external_wallet_service = external_wallet_service

    async def handle_incoming(
        self,
        tx_hash: str,
        address: str,
        coin: str,
        network: str,
        amount: Decimal,
        status_str: str = "pending_onchain"
    ) -> DepositLog:
        # 1) validate network and supported deposit token
        try:
            _ = self.registry.token_cfg(network, coin, "deposit")
            _ = self.registry.get_network(network)
        except UnknownNetworkError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Network {network} not supported"
            )
        except UnsupportedTokenError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token {coin} not depositable on {network}"
            )

        # 2) find external wallet by address and network
        wallet: Optional[ExternalWallet] = await ExternalWallet.find_one(
            (ExternalWallet.address == address) & (ExternalWallet.network == network)
        )
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="External wallet not found"
            )

        # 3) prevent duplicate deposit logs
        existing = await DepositLog.find_one(DepositLog.tx_hash == tx_hash)
        if existing:
            return existing

        # 4) record deposit log
        deposit = DepositLog(
            external_wallet_id=str(wallet.id),
            tx_hash=tx_hash,
            coin=coin,
            network=network,
            amount=amount,
            status=status_str,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        await deposit.insert()

        # 5) adjust internal USD balance after on-chain confirmation
        await InternalBalanceService.adjust_balance(
            wallet.user_id,
            coin,
            amount
        )

        return deposit

    async def get_deposit_status(self, log_id: str) -> DepositLog:
        log = await DepositLog.get(log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Deposit not found'
            )
        return log
    
    async def generate_address(
        self,
        user_id: int,
        network: str,
        token: str,
        wallet_type: str = "onchain"
    ) -> Dict:
        # 1) Валідація мережі й токена
        try:
            token_cfg = self.registry.token_cfg(network, token, "deposit")
            net_cfg = self.registry.get_network(network)
        except UnknownNetworkError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Network {network} not supported")
        except UnsupportedTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Token {token} not depositable on {network}")

        # 2) Генерація адреси через ExternalWalletService
        source = "telegram" if wallet_type == "telegram" else "manual"
        wallet = await self.external_wallet_service.create_external_wallet(
            user_id=str(user_id),
            coin=token,
            network=network,
            source=source
        )

        # 3) Генерація QR-коду
        qr_img = qrcode.make(wallet.address)
        buf = BytesIO()
        qr_img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        qr_code_url = f"data:image/png;base64,{qr_b64}"

        return {
            "external_wallet_id": str(wallet.id),
            "address": wallet.address,
            "qr_code_url": qr_code_url
        }

