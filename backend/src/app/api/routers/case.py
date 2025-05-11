from fastapi import APIRouter, Depends, HTTPException, status
from app.db.models.user import User
from app.api.deps import get_current_user
from app.schemas.case import CaseOpenRequest, CaseResult
from app.services.case_service import open_case

router = APIRouter()


@router.post("/cases/open", response_model=CaseResult)
def open_case_endpoint(
    data: CaseOpenRequest,
    user: User = Depends(get_current_user)
):
    try:
        result = open_case(user, data.case_id)
        return CaseResult(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
