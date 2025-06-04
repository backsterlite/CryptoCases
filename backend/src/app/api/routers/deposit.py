from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_network_registry, require_role
from app.config.network_registry import NetworkRegistry, UnknownNetworkError, UnsupportedTokenError
from app.services.deposit_service import DepositService
from app.schemas.deposit import(
    NetworkListResponse,
    TokenListResponse,
    TokenInfo,
    GenerateAddressRequest,
    GenerateAddressResponse,
    DepositHistoryResponse
)

router = APIRouter(prefix="/deposit", tags=["deposit"])

@router.get("/networks", response_model=NetworkListResponse)
def list_networks(
    registry: NetworkRegistry = Depends(get_network_registry)
):
    """List supported networks for deposits"""
    return {"networks": registry.list_network_codes()}

@router.get("/networks/{network}/tokens", response_model=TokenListResponse)
def list_tokens(
    network: str,
    registry: NetworkRegistry = Depends(get_network_registry)
):
    """List tokens available for deposit on a given network"""
    try:
        symbols = registry.list_tokens(network, "deposit")
        tokens = []
        for symbol in symbols:
            cfg = registry.token_cfg(network, symbol, "deposit")
            tokens.append(TokenInfo(symbol=symbol, decimals=cfg.decimals))
    except UnknownNetworkError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Network {network} not supported"
        )
    except UnsupportedTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error listing tokens for network {network}"
        )
    return {"network": network, "tokens": tokens}

@router.post("/address", response_model=GenerateAddressResponse)
async def generate_address(
    req: GenerateAddressRequest,
    user=Depends(require_role("user")),
    service: DepositService = Depends()
):
    """Generate or retrieve a deposit address for the user"""
    try:
        result = await service.generate_address(
            user_id=user["id"],
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

@router.get("/history", response_model=DepositHistoryResponse)
async def get_history(
    user=Depends(require_role("user")),
    service: DepositService = Depends()
):
    """Get deposit history for the current user"""
    history = await service.get_deposit_history(user_id=user["id"])
    return {"history": history}
