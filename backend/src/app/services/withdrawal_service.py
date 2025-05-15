from decimal import Decimal
from app.db.models.user import User
from app.db.models.withdrawal import WithdrawalLog
from app.services.wallet_service import has_sufficient_balance, WalletService
from app.services.coin_registry import CoinRegistry
from app.services.blockchain.evm_client import send_evm_token
from app.services.blockchain.tron_client import send_tron_token


class WithdrawalService:
    @staticmethod
    async def process_withdrawal(
        user: User,
        token: str,
        network: str,
        amount: Decimal,
        to_address: str
    ) -> str:
        """
        Returns: tx_hash or raises
        """
        token = token.upper()
        network = network.upper()

        if not CoinRegistry.is_supported(token, network):
            raise ValueError("Token/network not supported")

        if not has_sufficient_balance(user, token, network, amount):
            raise ValueError("Insufficient balance")

        # Get network type (EVM, TRON, etc.)
        coin = CoinRegistry.get(token)
        net_type = coin.coin_contract_addresses[network].type
        contract = CoinRegistry.get_contract(token, network)
        decimals = CoinRegistry.get_decimals(token, network)

        # Dispatch to correct blockchain client
        if net_type == "EVM":
            tx_hash = send_evm_token(to_address, contract, amount, decimals)
        elif net_type == "TRON":
            tx_hash = send_tron_token(to_address, contract, amount, decimals)
        else:
            raise NotImplementedError(f"Withdrawals not yet supported for {net_type}")

        # Deduct from balance
        await WalletService.update_coin_balance(
                telegram_id=user.user_id,
                coin_id=token,
                network=network,
                delta_str=f"-{amount}"
        )

        # (Optional) Log withdrawal
        # save_withdrawal(user.id, token, network, amount, to_address, tx_hash)
        log = WithdrawalLog(
            user_id=str(user.id),
            token=token,
            network=network,
            amount=str(amount),
            address=to_address,
            tx_hash=tx_hash
        )
        await log.insert()
        return tx_hash
