from decimal import Decimal
from fastapi import Depends, HTTPException, status
from typing import Optional

from app.services.internal_balance_service import InternalBalanceService
from app.services.rate_cache import rate_cache
from app.db.models.withdrawal_log import WithdrawalLog
from app.services.blockchain.factory import BlockchainClientFactory
from app.api.deps import get_network_registry
from app.config.network_registry import NetworkRegistry, UnknownNetworkError, UnsupportedTokenError
from app.config.settings import settings


class WithdrawalService:
    """
    Service for creating, approving, and processing user withdrawal requests.
    Relies on NetworkRegistry for on-chain configs and InternalBalanceService for USD reservations.
    """
    def __init__(
        self,
        registry: NetworkRegistry = Depends(get_network_registry),
    ):
        self.registry = registry

    async def deduct_internal_balance(self, user_id: int, amount_usd: Decimal) -> None:
        try:
            await InternalBalanceService.deduct_usd_amount(user_id, amount_usd)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def create_withdrawal_log(
        self,
        user_id: int,
        external_wallet_id: Optional[str],
        to_address: str,
        amount_usdt: Decimal,
        status_str: str,
        network: str,
        rate: Optional[Decimal] = None,
    ) -> WithdrawalLog:
        log = WithdrawalLog(
            user_id=user_id,
            external_wallet_id=external_wallet_id,
            network=network,
            to_address=to_address,
            amount_usdt=amount_usdt,
            conversion_rate=rate or Decimal("0"),
            status=status_str,
        )
        await log.insert()
        return log

    async def execute_transaction(self, log: WithdrawalLog, contract: str, decimals: int) -> str:
        try:
            factory = BlockchainClientFactory(registry=self.registry)
            client = factory.get_client(network_code=log.network)
            # convert to atomic units
            atomic_amount = int(log.amount_usdt * (10 ** decimals))
            unsigned = client.prepare_transaction(
                from_address=settings.PROJECT_WALLET_ADDRESS,
                to_address=log.to_address,
                amount=atomic_amount,
                contract=contract,
            )
            signed = client.sign_transaction(unsigned)
            return client.send_transaction(signed)
        except Exception as e:
            log.status = 'failed'
            await log.save()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Blockchain error: {e}'
            )

    async def create_withdrawal_request(
        self,
        user_id: int,
        coin: str,
        network: str,
        to_address: str,
        amount_usd: Decimal,
    ) -> WithdrawalLog:
        # 1) validate network and token
        try:
            token_cfg = self.registry.token_cfg(network, coin, "withdrawal")
            net_cfg = self.registry.get_network(network)
        except UnknownNetworkError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Network {network} not supported")
        except UnsupportedTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token {coin} not withdrawable on {network}")

        # 2) validate address format and existence
        factory = BlockchainClientFactory(registry=self.registry)
        client = factory.get_client(network_code=net_cfg.type)
        if not client.validate_address(to_address):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid address format")
        if net_cfg.existence_check and not client.exists_on_chain(to_address):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address does not exist on chain")

        # 3) deduct internal USD balance
        await self.deduct_internal_balance(user_id, amount_usd)

        # 4) fetch conversion rate
        rate = await rate_cache.get_rate(coin)

        # 5) create log in pending_review
        log = await self.create_withdrawal_log(
            user_id=user_id,
            external_wallet_id=None,
            to_address=to_address,
            amount_usdt=amount_usd,
            status_str="pending_review",
            network=network,
            rate=rate,
        )
        return log

    async def approve_withdrawal(self, log_id: str, admin_id: str) -> WithdrawalLog:
        log = await WithdrawalLog.get(log_id)
        if not log or log.status != 'pending_review':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Withdrawal not found or not pending_review'
            )
        # mark approved
        log.status = 'approved'
        log.admin_id = admin_id
        await log.save()

        # execute on-chain
        token_cfg = self.registry.token_cfg(log.network, log.coin_symbol, "withdrawal")
        tx_hash = await self.execute_transaction(log, token_cfg.contract, token_cfg.decimals)

        # update broadcasted
        log.tx_hash = tx_hash
        log.status = 'broadcasted'
        await log.save()
        return log

    async def process_auto_withdrawal(
        self,
        user_id: int,
        coin: str,
        network: str,
        to_address: str,
        amount_usd: Decimal,
    ) -> WithdrawalLog:
        # auto-flow: pending -> broadcasted
        # 1) validate & token_cfg
        try:
            token_cfg = self.registry.token_cfg(network, coin, "withdrawal")
            net_cfg = self.registry.get_network(network)
        except UnknownNetworkError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Network {network} not supported")
        except UnsupportedTokenError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token {coin} not withdrawable on {network}")

        # 2) address checks
        
        factory = BlockchainClientFactory(registry=self.registry)
        client = factory.get_client(network_code=net_cfg.type)
        if not client.validate_address(to_address) or (net_cfg.existence_check and not client.exists_on_chain(to_address)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or non-existent address")

        # 3) deduct balance
        await self.deduct_internal_balance(user_id, amount_usd)

        # 4) rate
        rate = await rate_cache.get_rate(coin)

        # 5) log pending
        log = await self.create_withdrawal_log(
            user_id=user_id,
            external_wallet_id=None,
            to_address=to_address,
            amount_usdt=amount_usd,
            status_str='pending',
            network=network,
            rate=rate,
        )

        # 6) execute transaction
        tx_hash = await self.execute_transaction(log, token_cfg.contract, token_cfg.decimals)
        log.tx_hash = tx_hash
        log.status = 'broadcasted'
        await log.save()
        return log

    async def get_withdrawal_status(self, log_id: str) -> WithdrawalLog:
        log = await WithdrawalLog.get(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Withdrawal not found')
        return log

    async def reject_withdrawal(self, log_id: str, admin_id: str) -> WithdrawalLog:
        log = await WithdrawalLog.get(log_id)
        if not log or log.status != 'pending_review':
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Withdrawal not found or not pending_review')
        log.status = 'rejected'
        log.admin_id = admin_id
        await log.save()
        return log
