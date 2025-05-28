from typing import List, Optional

from fastapi import HTTPException, Depends
from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError

from app.api.deps import get_hd_wallet_service
from app.db.models.external_wallet import ExternalWallet
from app.db.models.hd_wallet_meta import HDWalletMeta
from app.utils.hd_wallet import HDWalletService
from app.config.settings import settings


class ExternalWalletService:
    def __init__(
        self,
        hd_wallet: HDWalletService=Depends(get_hd_wallet_service)
        ):
        self._hd_wallet_service = hd_wallet

    async def create_external_wallet(self, user_id: str, coin: str, network: str, source: str) -> ExternalWallet:
        """
        Create new external wallet for user
        """
        try:
            # 1) Завантажуємо або ініціалізуємо HDWalletMeta
            meta = await HDWalletMeta.find_one({"coin": coin, "network": network})
            if not meta:
                # беремо XPUB із налаштувань динамічно
                env_key = f"XPUB_{coin}_{network}"
                xpub = getattr(settings, env_key)
                meta = HDWalletMeta(coin=coin, network=network, xpub=xpub, current_index=0)
                await meta.insert()

            # 2) Деривація адреси
            idx = meta.current_index
            path_template = settings.HD_DERIVATION_PATH_TEMPLATE
            address, full_path = self._hd_wallet_service.derive_address(meta.xpub, path_template, idx, network)

            # 3) Зберігаємо ExternalWallet з новим адресом
            wallet = ExternalWallet(
                user_id=user_id,
                coin=coin,
                network=network,
                address=address,
                source=source,
                vault_key_id=None,
                derivation_index=idx,
                derivation_path=full_path
            )
            await wallet.insert()

            # 4) Інкрементуємо current_index
            meta.current_index += 1
            await meta.save()

            return wallet

        except DuplicateKeyError:
            raise HTTPException(
                status_code=400,
                detail="Wallet with this address already exists"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create wallet: {str(e)}"
            )

    async def list_external_wallets(self, user_id: str) -> List[ExternalWallet]:
        """
        Get list of user's external wallets
        """
        try:
            return await ExternalWallet.find(ExternalWallet.user_id == user_id).to_list()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list wallets: {str(e)}"
            )

    async def remove_external_wallet(self, wallet_id: PydanticObjectId, user_id: str) -> None:
        """
        Remove external wallet
        """
        try:
            deleted = await ExternalWallet.find_one(
                (ExternalWallet.id == wallet_id) & (ExternalWallet.user_id == user_id)
            )
            if not deleted:
                raise HTTPException(status_code=404, detail="External wallet not found")
            await deleted.delete()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove wallet: {str(e)}"
            )