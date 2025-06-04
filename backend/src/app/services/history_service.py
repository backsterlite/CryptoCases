# src/app/services/history_service.py

from typing import List
from bson import ObjectId
from beanie import PydanticObjectId
from pymongo import DESCENDING

from app.db.models.player import SpinLog
from app.db.models.deposit_log import DepositLog
from app.db.models.withdrawal_log import WithdrawalLog
from app.schemas.history import (
    SpinHistoryItem,
    DepositHistoryItem,
    WithdrawalHistoryItem,
)

class HistoryService:
    @staticmethod
    async def get_spins(user_id: str, limit: int = 20, offset: int = 0) -> List[SpinHistoryItem]:
        """
        Повертає список останніх `limit` записів SpinLog для user_id.
        Відбираємо тільки потрібні клієнту поля.
        """
        # Припускаємо, що в моделі SpinLog є user_id (тип str або PydanticObjectId)
        # сортуємо за спаданням created_at
        query = SpinLog.find(
            {"user_id": user_id}
        ).sort([("created_at", DESCENDING)]).skip(offset*limit).limit(limit) # type: ignore

        docs = await query.to_list()
        result: List[SpinHistoryItem] = []
        for doc in docs:
            item = SpinHistoryItem(
                id=str(doc.id),
                case_id=doc.case_id,
                stake=doc.stake,
                payout=doc.payout,
                payout_usd=doc.payout_usd,
                prize_id=doc.prize_id,
                created_at=doc.created_at,
            )
            result.append(item)
        return result

    @staticmethod
    async def get_deposits(user_id: str, limit: int = 20, offset: int = 0) -> List[DepositHistoryItem]:
        """
        Повертає список останніх `limit` записів DepositLog для user_id.
        Відбираємо тільки потрібні клієнту поля.
        """
        # Передбачається, що DepositLog зберігає user_id при створенні
        query = DepositLog.find(
            {"user_id": user_id}
        ).sort([("created_at", DESCENDING)]).skip(offset*limit).limit(limit) # type: ignore

        docs = await query.to_list()
        result: List[DepositHistoryItem] = []
        for doc in docs:
            item = DepositHistoryItem(
                id=str(doc.id),
                coin=doc.coin,
                amount=doc.amount,
                status=doc.status,
                tx_hash=doc.tx_hash,
                confirmations=doc.confirmations,
                created_at=doc.created_at,
            )
            result.append(item)
        return result

    @staticmethod
    async def get_withdrawals(
        user_id: str, limit: int = 20,
        offset: int = 0
    ) -> List[WithdrawalHistoryItem]:
        """
        Повертає список останніх `limit` записів WithdrawalLog для user_id.
        Відбираємо тільки потрібні клієнту поля.
        """
        query = WithdrawalLog.find(
            {"user_id": user_id}
        ).sort([("created_at", DESCENDING)]).skip(offset*limit).limit(limit) # type: ignore

        docs = await query.to_list()
        result: List[WithdrawalHistoryItem] = []
        for doc in docs:
            item = WithdrawalHistoryItem(
                id=str(doc.id),
                to_address=doc.to_address,
                amount_coin=doc.amount_coin,
                fee_coin=doc.fee_coin,
                status=doc.status,
                tx_hash=doc.tx_hash,
                confirmations=doc.confirmations,
                created_at=doc.created_at,
            )
            result.append(item)
        return result
