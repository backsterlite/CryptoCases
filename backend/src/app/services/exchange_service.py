
from typing import Optional, Tuple
from decimal import Decimal

from fastapi import HTTPException, status

from app.core.config.coin_registry import CoinRegistry
from app.core.config.asset_registry import AssetRegistry
from app.core.config.settings import get_settings
from app.db.transaction import TransactionManager
from app.services.rate_cache import rate_cache
from app.services.internal_balance_service import InternalBalanceService
from app.models.coin import Coin, CoinAmount
from app.schemas.wallet import ExchangeQuoteRequest, ExchangeExecuteRequest
from app.utils import coin_keys

class ExchangeService:
    _settings = get_settings()
    
    @classmethod
    def validate(cls, data: ExchangeQuoteRequest | ExchangeExecuteRequest):
        cls._validate_token_exists(data.from_token)
        cls._validate_token_exists(data.to_token)
        cls._validate_network_for_token(data.from_token, data.from_network)
        cls._validate_network_for_token(data.to_token, data.to_network)
        cls._validate_different_tokens(
            from_symbol=data.from_token,
            from_network=data.from_network,
            to_symbol=data.to_token,
            to_network=data.to_network
        )
    
    @classmethod
    def _validate_token_exists(cls, token_symbol: str) -> None:
        """
        Verify that `token_symbol` corresponds to a known coin in CoinRegistry.
        Raises HTTPException if coin is not found.
        """
        print("TOKEN SYMBOL:", token_symbol)
        if CoinRegistry.get(token_symbol) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported token: {token_symbol}"
            )

    @classmethod
    def _validate_network_for_token(cls, token_symbol: str, network: Optional[str]) -> None:
        """
        Ensure that `network` is valid for `token_symbol`. 
        - If network is None, token must be one of the canonical tokens (USDT or USDC).
        - If network is provided, AssetRegistry must have a contract for (token, network).
        Raises HTTPException on invalid combination.
        """
        print("TOKEN SYMBOL:", token_symbol, "network", network)
        # If no network, token must be USDT or USDC (internal balances are network-agnostic)
        if network is None:
            if coin_keys.to_id(token_symbol) not in cls._settings.GLOBAL_USD_WALLET_ALIAS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Token {token_symbol} requires a network. "
                        "Only USDT/USDC can omit network."
                    )
                )
            return

        # If network is specified, token must exist on that chain
        allow = AssetRegistry.is_supported(
            coin_id=coin_keys.to_asset_key(token_symbol),
            chain=network)
        if not allow:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Token {token_symbol} is not supported on network {network}"
            )

    @classmethod
    def _validate_different_tokens(
        cls,
        from_symbol: str,
        from_network: Optional[str],
        to_symbol: str,
        to_network: Optional[str]
    ) -> None:
        """
        Ensure that the source and target token+network pair are not identical.
        Raises HTTPException if user attempts to swap a token onto itself.
        """
        if from_symbol == to_symbol and from_network == to_network:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="`from_token` and `to_token` (with networks) must differ"
            )
            
    @classmethod
    async def get_rates_or_503(
        cls,
        from_symbol: str,
        to_symbol: str
    ) -> Tuple[Decimal, Decimal]:
        """
        Returns the rates (USD) for two coins (sell and buy).
        If at least one rate is missing or zero → throws 503 Service Unavailable.
        """
        # 1. Шукаємо coingecko_id через CoinRegistry
        from_meta = CoinRegistry.get(from_symbol)
        to_meta = CoinRegistry.get(to_symbol)

        if from_meta is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported token: {from_symbol}"
            )
        if to_meta is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported token: {to_symbol}"
            )

        # 2. Приводимо coingecko_id до нижнього регістру
        from_id = from_meta.coingecko_id.lower()
        to_id = to_meta.coingecko_id.lower()

        # 3. Запитуємо курси в кеша
        rate_from: Decimal = await rate_cache.get_rate(from_id)
        rate_to: Decimal = await rate_cache.get_rate(to_id)

        # 4. Якщо будь-який курс ≡ 0 → 503 Service Unavailable
        if rate_from == 0 or rate_to == 0:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="One or both rates are unavailable"
            )

        return rate_from, rate_to
    
    @classmethod
    async def ensure_sufficient_balance(
        cls,
        user_id: int,
        token: str,
        network: str | None,
        required_amount: Decimal
    ) -> Decimal:
        """
        Fetch the user's balance for `token` (on `network` or canonical) and ensure
        it is at least `required_amount`. If not, raise HTTPException 400.
        Returns the current balance (Decimal).
        """
        # Fetch current balance (for USDT/USDC, network should be None)
        current_balance: Decimal = await InternalBalanceService.get_balance(
            user_id=user_id,
            network=network,
            coin=coin_keys.to_id(token)
        )

        if current_balance < required_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance: have {current_balance} {token}, "
                       f"need {required_amount}"
            )

        return current_balance
    
    
    @classmethod
    def calculate_to_amount(
        cls,
        from_symbol: str,
        from_network: str | None,
        to_symbol: str,
        to_network: str | None,
        from_amount: Decimal,
        rate_from_usd: Decimal,
        rate_to_usd: Decimal
    ) -> Decimal:
        """
        Convert `from_amount` of (from_symbol, from_network) into `to_amount` of (to_symbol, to_network),
        using CoinAmount.to_usd() і CoinAmount.amount_from_usd().
        """
        # 1) Створюємо моделі Coin і CoinAmount для вихідного токена
        from_coin = Coin.from_id(from_symbol)
        from_coin_amount = CoinAmount(coin=from_coin, network=from_network or from_coin.native_network, amount=from_amount)
        
        # 2) Перетворюємо to USD
        usd_value = from_coin_amount.to_usd(rate_from_usd)  
        #    → округлено всередині to_usd() до TARGET_SCALE = Decimal("0.000001")

        # 3) Отримуємо точну кількість токена-одержувача
        to_amount = CoinAmount.amount_from_usd(
            coin_id=to_symbol,
            network=to_network or Coin.from_id(to_symbol).native_network,
            value_in_usd=usd_value,
            rate=rate_to_usd
        )
        return to_amount
    
    @classmethod
    async def quote(
        cls,
        from_token: str,
        from_network: str | None,
        to_token: str,
        to_network: str | None,
        from_amount: Decimal
    ) -> Decimal:
        """
        Return the estimated `to_amount` given `from_amount` of (from_token, from_network).
        No balance changes.
        """
        rate_from, rate_to = await cls.get_rates_or_503(from_token, to_token)
        to_amount = cls.calculate_to_amount(
            from_amount=from_amount,
            rate_from_usd=rate_from,
            rate_to_usd=rate_to,
            from_symbol=from_token,
            from_network=from_network,
            to_symbol=to_token,
            to_network=to_network)
        return to_amount

    @classmethod
    async def execute(
        cls,
        user_id: int,
        from_token: str,
        from_network: str | None,
        to_token: str,
        to_network: str | None,
        from_amount: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Perform the actual exchange:
        - Validate rates, balance.
        - Deduct from (from_token, from_network).
        - Credit to (to_token, to_network).
        - Return (from_amount, to_amount, updated_from_balances, updated_to_balances).
        """
        # 1) Fetch rates (or 503)
        rate_from, rate_to = await cls.get_rates_or_503(from_token, to_token)

        # 2) Ensure sufficient balance of from_token
        await cls.ensure_sufficient_balance(
            user_id=user_id,
            token=from_token,
            network=from_network,
            required_amount=from_amount)

        # 3) Calculate to_amount
        to_amount = cls.calculate_to_amount(
            from_amount=from_amount,
            rate_from_usd=rate_from,
            rate_to_usd=rate_to,
            from_symbol=from_token,
            from_network=from_network,
            to_symbol=to_token,
            to_network=to_network)

        # 4) Perform balance updates (atomicity depends on DB capabilities)
        # Deduct from “from_token”
        tx = TransactionManager()
        async with tx() as session:
            
            await InternalBalanceService.adjust_balance(
                user_id=user_id,
                coin=from_token, 
                network=from_network, 
                delta=-from_amount,
                session=session
            )
            # Credit “to_token”
            await InternalBalanceService.adjust_balance(
                user_id=user_id,
                coin=to_token,
                network=to_network,
                delta=to_amount,
                session=session
            )

        return from_amount, to_amount