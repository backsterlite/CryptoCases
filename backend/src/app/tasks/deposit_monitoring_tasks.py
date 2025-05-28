from celery import shared_task
from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Optional

from app.db.models.external_wallet import ExternalWallet
from app.db.models.deposit_log import DepositLog
from app.services.blockchain.factory import BlockchainClientFactory
from app.api.deps import get_network_registry
from app.services.rate_cache import rate_cache
from app.services.internal_balance_service import InternalBalanceService
from app.services.deposit_service import DepositService

logger = logging.getLogger(__name__)

@shared_task(name="monitor_deposits")
async def monitor_deposits():
    """
    Моніторинг депозитів для всіх мереж
    """
    try:
        # Використовуємо кешований NetworkRegistry
        registry = get_network_registry()
        factory = BlockchainClientFactory(registry)
        deposit_service = DepositService(registry=registry)

        # Отримуємо всі активні гаманці
        wallets = await ExternalWallet.find().to_list()
        
        for wallet in wallets:
            try:
                # Отримуємо клієнт для відповідної мережі
                client = factory.get_client(wallet.network)
                
                # Отримуємо останній оброблений блок
                last_log = await DepositLog.find(
                    (DepositLog.external_wallet_id == str(wallet.id)) &
                    (DepositLog.network == wallet.network)
                ).sort(-DepositLog.block_number).first()
                
                from_block = last_log.block_number if last_log else None
                
                # Отримуємо транзакції
                transactions = client.get_transactions(wallet.address, from_block)
                
                for tx in transactions:
                    try:
                        # Перевіряємо чи транзакція вже оброблена
                        existing = await DepositLog.find_one(DepositLog.tx_hash == tx['hash'])
                        if existing:
                            continue
                            
                        # Отримуємо курс конвертації в USD
                        usd_rate = await rate_cache.get_rate(wallet.coin)
                        amount_usd = Decimal(tx['value']) * usd_rate
                        
                        # Створюємо запис в DepositLog через сервіс
                        deposit = await deposit_service.handle_incoming(
                            tx_hash=tx['hash'],
                            address=wallet.address,
                            coin=wallet.coin,
                            network=wallet.network,
                            amount=Decimal(tx['value']),
                            status_str='pending_onchain'
                        )
                        
                        logger.info(
                            f"Processed deposit: {tx['hash']} for user {wallet.user_id}, "
                            f"amount: {tx['value']} {wallet.coin} (${amount_usd})"
                        )
                        
                    except Exception as e:
                        logger.error(f"Error processing transaction {tx['hash']}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing wallet {wallet.address}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in monitor_deposits task: {str(e)}")
    finally:
        factory.close_all()

@shared_task(name="confirm_deposits")
async def confirm_deposits():
    """
    Підтвердження депозитів з достатньою кількістю підтверджень
    """
    try:
        # Використовуємо кешований NetworkRegistry
        registry = get_network_registry()
        factory = BlockchainClientFactory(registry)
        
        # Отримуємо всі pending депозити
        pending_deposits = await DepositLog.find(
            DepositLog.status == 'pending_onchain'
        ).to_list()
            
        for deposit in pending_deposits:
            try:
                # Отримуємо клієнт для відповідної мережі
                client = factory.get_client(deposit.network)
                
                # Отримуємо необхідну кількість підтверджень для мережі
                required_confirmations = registry.get_network(deposit.network).required_confirmations
                
                # Перевіряємо підтвердження
                if client.is_transaction_confirmed(deposit.tx_hash, required_confirmations):
                    deposit.status = 'confirmed'
                    await deposit.save()
                    
                    logger.info(f"Deposit {deposit.tx_hash} confirmed")
                    
            except Exception as e:
                logger.error(f"Error confirming deposit {deposit.tx_hash}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in confirm_deposits task: {str(e)}")
    finally:
        factory.close_all() 