from celery import shared_task
from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Optional, Dict, List, Tuple

from app.db.models.external_wallet import ExternalWallet
from app.db.models.withdrawal_log import WithdrawalLog
from app.services.blockchain.factory import BlockchainClientFactory
from app.services.blockchain.base import IBlockchainClient
from app.core.config.network_registry import NetworkRegistry
from app.api.deps import get_network_registry
from app.services.rate_cache import rate_cache
from app.services.internal_balance_service import InternalBalanceService

logger = logging.getLogger(__name__)

# Константи для мінімальних балансів
MIN_BALANCES = {
    "ETH": Decimal("0.01"),  # Мінімальний баланс для gas
    "BNB": Decimal("0.01"),  # Мінімальний баланс для gas
    "MATIC": Decimal("0.01"),  # Мінімальний баланс для gas
    "TON": Decimal("0.1"),  # Мінімальний баланс для активності
    "TRX": Decimal("1"),  # Мінімальний баланс для ресурсів
    "SOL": Decimal("0.01"),  # Мінімальний баланс для rent
}

async def get_wallet_balances(
    client: IBlockchainClient,
    address: str,
    network: str,
    registry: NetworkRegistry
) -> List[Tuple[str, Decimal]]:
    """
    Отримати баланси всіх доступних монет на адресі
    """
    balances = []
    
    # Отримуємо список доступних монет для мережі
    network_cfg = registry.get_network(network)
    
    for token in network_cfg.list_tokens("deposit"):
        try:
            balance = await client.get_balance(
                address=address,
                symbol=token.symbol,
                is_deposit=True
            )
            
            if balance > 0:
                balances.append((token.symbol, balance))
                
        except Exception as e:
            logger.error(f"Error getting balance for {token.symbol} on {address}: {str(e)}")
            continue
            
    return balances

@shared_task(name="sweep_derived_addresses")
async def sweep_derived_addresses():
    """
    Sweep балансів з похідних HD гаманців на основний HOT гаманець
    """
    try:
        # Використовуємо кешований NetworkRegistry
        registry = get_network_registry()
        factory = BlockchainClientFactory(registry)
        
        # Отримуємо всі похідні адреси
        derived_wallets = await ExternalWallet.find(
            (ExternalWallet.derivation_index != None) &  # це похідна адреса
            (ExternalWallet.is_active == True)  # активна адреса
        ).to_list()
        
        # Групуємо гаманці за мережею для оптимізації
        wallets_by_network: Dict[str, List[ExternalWallet]] = {}
        for wallet in derived_wallets:
            if wallet.network not in wallets_by_network:
                wallets_by_network[wallet.network] = []
            wallets_by_network[wallet.network].append(wallet)
        
        # Обробляємо кожну групу гаманців
        for network, wallets in wallets_by_network.items():
            try:
                # Отримуємо клієнт для мережі
                client = factory.get_client(network)
                
                # Обробляємо кожен гаманець
                for wallet in wallets:
                    try:
                        # Отримуємо баланси всіх монет на адресі
                        balances = await get_wallet_balances(
                            client=client,
                            address=wallet.address,
                            network=network,
                            registry=registry
                        )
                        
                        for coin, balance in balances:
                            try:
                                # Отримуємо HOT гаманець для цієї монети/мережі
                                hot_wallet = await ExternalWallet.find_one(
                                    (ExternalWallet.coin == coin) &
                                    (ExternalWallet.network == network) &
                                    (ExternalWallet.is_hot == True)
                                )
                                
                                if not hot_wallet:
                                    logger.error(f"No hot wallet found for {coin} on {network}")
                                    continue
                                    
                                # Визначаємо мінімальний баланс для мережі
                                min_balance = MIN_BALANCES.get(coin, Decimal("0"))
                                
                                # Якщо баланс достатній для sweep
                                if balance > min_balance:
                                    # Визначаємо суму для sweep
                                    sweep_amount = balance - min_balance
                                    
                                    # Отримуємо оцінку gas
                                    gas_estimate = await client.estimate_sweep_gas(
                                        from_address=wallet.address,
                                        to_address=hot_wallet.address,
                                        amount=sweep_amount,
                                        symbol=coin
                                    )
                                    
                                    # Перевіряємо чи достатньо балансу з урахуванням gas
                                    if sweep_amount > gas_estimate:
                                        # Створюємо транзакцію sweep
                                        tx_hash = await client.sweep_balance(
                                            from_address=wallet.address,
                                            to_address=hot_wallet.address,
                                            amount=sweep_amount,
                                            symbol=coin
                                        )
                                        
                                        # Записуємо в лог
                                        await WithdrawalLog.create(
                                            from_wallet_id=str(wallet.id),
                                            to_wallet_id=str(hot_wallet.id),
                                            tx_hash=tx_hash,
                                            amount=sweep_amount,
                                            status='pending',
                                            network=network,
                                            coin=coin,
                                            created_at=datetime.now(timezone.utc)
                                        )
                                        
                                        logger.info(
                                            f"Sweep created: {tx_hash} from {wallet.address} "
                                            f"to {hot_wallet.address}, amount: {sweep_amount} {coin}"
                                        )
                                    else:
                                        logger.info(
                                            f"Insufficient balance for sweep on {wallet.address}: "
                                            f"balance={balance}, gas_estimate={gas_estimate} {coin}"
                                        )
                                        
                            except Exception as e:
                                logger.error(f"Error processing {coin} sweep for {wallet.address}: {str(e)}")
                                continue
                                
                    except Exception as e:
                        logger.error(f"Error processing wallet {wallet.address}: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing network {network}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in sweep_derived_addresses task: {str(e)}")
    finally:
        factory.close_all()

@shared_task(name="confirm_sweeps")
async def confirm_sweeps():
    """
    Підтвердження sweep транзакцій
    """
    try:
        registry = get_network_registry()
        factory = BlockchainClientFactory(registry)
        
        # Отримуємо всі pending sweep транзакції
        pending_sweeps = await WithdrawalLog.find(
            (WithdrawalLog.status == 'pending') &
            (WithdrawalLog.from_wallet_id != None)  # це sweep транзакція
        ).to_list()
        
        for sweep in pending_sweeps:
            try:
                # Отримуємо клієнт для мережі
                client = factory.get_client(sweep.network)
                
                # Отримуємо необхідну кількість підтверджень
                required_confirmations = registry.get_network(sweep.network).required_confirmations
                
                # Перевіряємо підтвердження
                if client.is_transaction_confirmed(sweep.tx_hash, required_confirmations):
                    sweep.status = 'confirmed'
                    await sweep.save()
                    
                    logger.info(f"Sweep {sweep.tx_hash} confirmed")
                    
            except Exception as e:
                logger.error(f"Error confirming sweep {sweep.tx_hash}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in confirm_sweeps task: {str(e)}")
    finally:
        factory.close_all() 