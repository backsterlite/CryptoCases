from decimal import Decimal
from typing import List

from fastapi import (
    APIRouter,
    Depends,
    Query,
    HTTPException,
    status
    )

from app.config.network_registry import NetworkRegistry, TokenCfg
from app.config.constants import WITHDRAWAL
from app.schemas.wallet import TokenInfo, TokenListResponse
from app.schemas.wallet import WithdrawalAddressRequest, WithdrawalAddressResponse
from app.api.deps import require_role, get_network_registry
from app.db.models.user import User

from . import API_V1

router = APIRouter(prefix=f"{API_V1}", tags=["Withdrawals"])





@router.get("/withdraw/options", response_model=List[TokenListResponse])
async def withdraw_options(
    user: User = Depends(require_role("user")),
    registry: NetworkRegistry = Depends(get_network_registry)
    ):
    """List available networks and tokens for withdrawal."""
    networks = registry.list_network_codes()
    resp: List[TokenListResponse] = []
    for net in networks:
        network = registry.get_network(code=net)
        tokens_code = network.list_tokens(op=WITHDRAWAL)
        tokens: List[TokenCfg] = [network.token_cfg(token_code, WITHDRAWAL) for token_code in tokens_code]
        resp.append(TokenListResponse(
            network=net.title(),
            tokens=[
                TokenInfo(
                    symbol=token.symbol,
                    contract=token.contract,
                    decimals=token.decimals
                ) for token in tokens 
            ]
        ))
    return resp

@router.get("/withdrawal/addresses", response_model=List[str])
async def list_withdrawal_addresses(
    network: str = Query(..., description="Network code, e.g. 'ton'"),
    current_user: User = Depends(require_role("user")),
    svc: WalletService = Depends()
):
    """List user's whitelisted withdrawal addresses for a network."""
    addrs = await svc.list_external_withdrawal_addresses(
        user_id=current_user.id,
        network=network
    )
    return addrs

@router.post("/withdrawal/addresses", response_model=WithdrawalAddressResponse, status_code=status.HTTP_201_CREATED)
async def add_withdrawal_address(
    req: WithdrawalAddressRequest,
    current_user = Depends(require_role("user")),
    svc: WalletService = Depends()
):
    """Whitelist a new withdrawal address."""
    addr = await svc.add_withdrawal_address(
        user_id=current_user.id,
        network=req.network,
        address=req.address
    )
    return WithdrawalAddressResponse(address=addr)