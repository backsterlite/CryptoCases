from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import(
    get_network_registry,
    require_role,
    get_deposit_service
    ) 
from app.config.network_registry import NetworkRegistry, UnknownNetworkError, UnsupportedTokenError, TokenCfg
from app.services.deposit_service import DepositService
from app.schemas.deposit import(
    GenerateAddressRequest,
    GenerateAddressResponse,
)
from app.schemas.wallet import TokenListResponse, TokenInfo
from . import API_V1


router = APIRouter(prefix=f"{API_V1}/deposit", tags=["deposit"])

@router.get("/deposit/options", response_model=List[TokenListResponse])
async def deposit_options(
    registry: NetworkRegistry = Depends(get_network_registry)
):
    """List available networks and tokens for deposit."""
    networks = registry.list_network_codes()
    resp: List[TokenListResponse] = []
    for net in networks:
        network = registry.get_network(code=net)
        tokens_code = network.list_tokens(op="deposit")
        tokens: List[TokenCfg] = [network.token_cfg(token_code, "deposit") for token_code in tokens_code]
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

@router.post("/address", response_model=GenerateAddressResponse)
async def generate_address(
    req: GenerateAddressRequest,
    user=Depends(require_role("user")),
    service: DepositService = Depends(get_deposit_service)
):
    """Generate or retrieve a deposit address for the user"""
    try:
        result = await service.generate_address(
            user_id=user.user_id,
            network=req.network,
            token=req.token,
            wallet_type=req.wallet_type
        )
        return result
    except UnknownNetworkError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {req.network} not supported"
        )
    except UnsupportedTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token {req.token} not depositable on {req.network}"
        )
