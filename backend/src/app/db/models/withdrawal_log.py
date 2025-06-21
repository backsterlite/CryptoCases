# src/app/models/withdrawal_log.py

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Literal

from beanie import Document, PydanticObjectId
from pydantic import Field

from app.models.history_status import StatusHistoryEntry


class WithdrawalLog(Document):
    user_id: int                     # ID користувача, який ініціює вивід
    external_wallet_id: str          # звідки (з якого гаманця) робимо вивід
    network: str                     # блокчейн-мережа (наприклад, "ethereum", "tron" тощо)
    to_address: str                  # адреса, куди відправимо кошти
    amount_coin: Decimal             # сума у native-одиницях токена
    amount_usdt: Decimal             # USDT-еквівалент для бухобліку
    conversion_rate: Decimal         # курс, за яким розраховано amount_usdt
    fee_coin: Optional[Decimal] = None
    fee_usdt: Optional[Decimal] = None
    tx_hash: Optional[str] = None
    block_number: Optional[int] = None
    confirmations: int = 0
    status: Literal[
        "pending",           # заявка подана, чекає перевірки
        "approved",          # схвалено адміном/системою, чекає broadcast
        "broadcasted",       # транзакція відправлена в мережу, чекає підтверджень
        "confirmed",         # підтверджено on-chain
        "rejected"           # відхилено на етапі перевірки (KYC/баланс/адаптер)
    ] = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # ————————————————
    # **новий блок**: масив історії змін статусу
    status_history: List[StatusHistoryEntry] = Field(default_factory=list)
    # ————————————————

    class Settings:
        name = "withdrawal_logs"
        indexes = [
            # індекс по user_id + created_at для швидкого списку всіх виводів користувача
            [("user_id", 1), ("created_at", -1)],
            # індекс для пошуку конкретної транзакції по tx_hash (якщо tx_hash не None)
            [("tx_hash", 1)],
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
        Оновлює статус виводу:  
         1) ставить new_status у self.status  
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
