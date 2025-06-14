# src/app/services/history_service.py

from typing import List, Dict, Optional
from bson import ObjectId
from beanie import PydanticObjectId

from app.db.models.player import SpinLog
from app.db.models.deposit_log import DepositLog
from app.db.models.withdrawal_log import WithdrawalLog
from app.schemas.history import (
    SpinHistoryItem,
    DepositHistoryItem,
    WithdrawalHistoryItem,
)
from app.schemas.admin.history.deposit import DepositHistoryEntry
from app.schemas.admin.history.spin import SpinLogEntry
from app.schemas.admin.history.withdrawal import WithdrawalHistoryEntry
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
        ).sort("-created_at").skip(offset*limit).limit(limit) # type: ignore

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
        ).sort("-created_at").skip(offset*limit).limit(limit) # type: ignore

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
        ).sort("-created_at").skip(offset*limit).limit(limit) # type: ignore

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
    
    @staticmethod
    async def get_spins_admin(
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> List[SpinLogEntry]:
        """
        Return full spin logs for admin, including all fields, optionally filtered by user_id.
        """
        filters: Dict[str, str] = {}
        if user_id:
            filters["user_id"] = user_id

        query = (
            SpinLog.find(filters)
            .sort("-created_at")
            .skip(offset * limit)
            .limit(limit)
        )  # type: ignore
        docs = await query.to_list()

        result: List[SpinLogEntry] = []
        for doc in docs:
            entry = SpinLogEntry(
                id=str(doc.id),
                user_id=doc.user_id,
                case_id=doc.case_id,
                server_seed_id=doc.server_seed_id,
                server_seed_hash=doc.server_seed_hash,
                server_seed_seed=doc.server_seed_seed,
                client_seed=doc.client_seed,
                nonce=doc.nonce,
                hmac_value=doc.hmac_value,
                raw_roll=doc.raw_roll,
                table_id=doc.table_id,
                odds_version=doc.odds_version,
                case_tier=doc.case_tier,
                prize_id=doc.prize_id,
                stake=doc.stake,
                payout=doc.payout,
                payout_usd=doc.payout_usd,
                pity_before=doc.pity_before,
                pity_after=doc.pity_after,
                rtp_session=doc.rtp_session,
                created_at=doc.created_at,
            )
            result.append(entry)

        return result

    @staticmethod
    async def get_deposits_admin(
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> List[DepositHistoryEntry]:
        """
        Return full deposit logs for admin, including status_history, optionally filtered by user_id.
        """
        filters: Dict[str, str] = {}
        if user_id:
            filters["user_id"] = user_id

        query = (
            DepositLog.find(filters)
            .sort("-created_at")
            .skip(offset * limit)
            .limit(limit)
        )  # type: ignore
        docs = await query.to_list()

        result: List[DepositHistoryEntry] = []
        for doc in docs:
            entry = DepositHistoryEntry(
                id=str(doc.id),
                user_id=doc.user_id,
                external_wallet_id=doc.external_wallet_id,
                tx_hash=doc.tx_hash,
                coin=doc.coin,
                amount=doc.amount,
                from_address=doc.from_address,
                block_number=doc.block_number,
                timestamp=doc.timestamp,
                confirmations=doc.confirmations,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                status_history=doc.status_history or [],
            )
            result.append(entry)

        return result

    @staticmethod
    async def get_withdrawals_admin(
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
    ) -> List[WithdrawalHistoryEntry]:
        """
        Return full withdrawal logs for admin, including status_history, optionally filtered by user_id.
        """
        filters: Dict[str, str] = {}
        if user_id:
            filters["user_id"] = user_id

        query = (
            WithdrawalLog.find(filters)
            .sort("-created_at")
            .skip(offset * limit)
            .limit(limit)
        )  # type: ignore
        docs = await query.to_list()

        result: List[WithdrawalHistoryEntry] = []
        for doc in docs:
            entry = WithdrawalHistoryEntry(
                id=str(doc.id),
                user_id=doc.user_id,
                external_wallet_id=doc.external_wallet_id,
                network=doc.network,
                to_address=doc.to_address,
                amount_coin=doc.amount_coin,
                amount_usdt=doc.amount_usdt,
                conversion_rate=doc.conversion_rate,
                fee_coin=doc.fee_coin,
                fee_usdt=doc.fee_usdt,
                tx_hash=doc.tx_hash,
                block_number=doc.block_number,
                confirmations=doc.confirmations,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                status_history=doc.status_history or [],
            )
            result.append(entry)

        return result