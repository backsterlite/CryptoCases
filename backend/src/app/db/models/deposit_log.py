# src/app/models/deposit_log.py

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Literal, List

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.history_status import StatusHistoryEntry


class DepositLog(Document):
    user_id: Optional[str]           # тепер можна довантажувати (якщо ExternalWallet не завжди повідомляє)
    external_wallet_id: str          # посилання на зовнішній гаманець
    tx_hash: str                     # хеш транзакції on-chain
    coin: str                        # символ токена, наприклад "USDT"
    amount: Decimal                  # сума депозиту у native-одиницях токена
    from_address: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None   # час підтвердження блоку
    confirmations: int = 0                 # скільки підтверджень вже зібрано
    status: Literal[
        "pending_onchain",     # згенеровано record, очікується on-chain
        "pending_internal",    # підтверджено on-chain, але ще не зараховано внутрішньо
        "confirmed",           # успішно зараховано внутрішньо
        "failed",              # відхилено / помилка
    ] = "pending_onchain"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ————————————————
    # **новий блок**: масив історії статусів
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)
    # ————————————————

    class Settings:
        name = "deposit_logs"
        indexes = [
            # індекс по user_id і даті створення для швидкого вибору списку всіх депозитів користувача
            [("user_id", 1), ("created_at", -1)],
            # індекс по tx_hash для унікальності/швидкого пошуку дублю (якщо треба)
            [("tx_hash", 1)],
            # можемо підключити compound-index по external_wallet_id + status, якщо потрібен
            [("external_wallet_id", 1), ("status", 1)],
        ]

    def update_status(
        self,
        new_status: str,
        actor_id: Optional[str] = None,
        actor_role: Optional[str] = None,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        country: Optional[str] = None,
    ) -> None:
        """
        Метод для зручного оновлення статусу:
        1) ставить новий статус у self.status
        2) додає запис у self.status_history
        3) оновлює updated_at
        """
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        entry = StatusHistoryEntry(
            status=new_status,
            changed_at=now,
            actor_id=actor_id,
            actor_role=actor_role,
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
            country=country,
        )
        self.status = new_status # type: ignore
        self.updated_at = now
        self.status_history.append(entry)
