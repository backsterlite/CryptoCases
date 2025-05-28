from celery import shared_task
from datetime import datetime, timezone
from decimal import Decimal
import logging
import asyncio

from app.db.init_db import init_db
from app.db.models.external_wallet import ExternalWallet
from app.db.models.deposit_log import DepositLog
from app.services.blockchain.factory import BlockchainClientFactory
from app.config.network_registry import NetworkRegistry
from app.services.rate_cache import rate_cache
from app.services.internal_balance_service import InternalBalanceService

logger = logging.getLogger(__name__)

@shared_task(name="monitor_deposits")
def monitor_deposits():
    asyncio.run(_monitor_deposits())

async def _monitor_deposits():
    await init_db()
    registry = NetworkRegistry()
    factory = BlockchainClientFactory(registry)

    # 1. Всі похідні (HD) гаманці
    wallets = await ExternalWallet.find().to_list()
    for wallet in wallets:
        try:
            client = factory.get_client(wallet.network)
            # 2. Останній оброблений блок
            last_log = await DepositLog.find(
                (DepositLog.external_wallet_id == str(wallet.id)) &
                (DepositLog.network == wallet.network)
            ).sort(-DepositLog.block_number).first()
            from_block = last_log.block_number if last_log else None

            # 3. Вхідні транзакції
            txs = client.get_transactions(wallet.address, from_block)
            for tx in txs:
                # 4. Чи вже є в DepositLog
                exists = await DepositLog.find_one(DepositLog.tx_hash == tx['hash'])
                if exists:
                    continue

                # 5. В якій монеті
                coin = wallet.coin
                network = wallet.network

                # 6. Курс до USD
                usd_rate = await rate_cache.get_rate(coin)
                amount_usd = Decimal(tx['value']) * usd_rate

                # 7. Створити DepositLog
                deposit = DepositLog(
                    external_wallet_id=str(wallet.id),
                    tx_hash=tx['hash'],
                    coin=coin,
                    amount=Decimal(tx['value']),
                    from_address=tx.get('from'),
                    block_number=tx.get('block_number'),
                    timestamp=datetime.fromtimestamp(tx.get('timestamp', datetime.now().timestamp()), tz=timezone.utc),
                    confirmations=tx.get('confirmations', 0),
                    status='pending_onchain'
                )
                await deposit.insert()

                # 8. Оновити внутрішній баланс
                await InternalBalanceService.adjust_balance(wallet.user_id, coin, Decimal(tx['value']))

                logger.info(f"Deposit {tx['hash']} for user {wallet.user_id} ({coin}) на {tx['value']} (${amount_usd})")
        except Exception as e:
            logger.error(f"Error for wallet {wallet.address}: {e}")
    factory.close_all()