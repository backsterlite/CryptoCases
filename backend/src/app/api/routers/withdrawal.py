from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from app.schemas.wallet import WithdrawalRequest
from app.services.withdrawal_service import WithdrawalService
from app.api.deps import require_role
from app.db.models.user import User

router = APIRouter(prefix="/withdraw", tags=["Withdrawals"])


@router.post("/", response_model=str)
def withdraw(
    data: WithdrawalRequest,
    user: User = Depends(require_role("user"))
):
    try:
        tx_hash = WithdrawalService.process_withdrawal(
            user=user,
            token=data.token,
            network=data.network,
            amount=Decimal(data.amount),
            to_address=data.address
        )
        return tx_hash
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e))
