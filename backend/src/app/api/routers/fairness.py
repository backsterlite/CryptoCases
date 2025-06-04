# routers/fairness.py
import os
import hashlib

from fastapi import APIRouter, Path, HTTPException, Depends
from fastapi.responses import RedirectResponse
from beanie import PydanticObjectId
from app.services.odds_service import export_odds
from app.db.models.player import ServerSeed, SpinLog
from app.schemas.case import CommitOut, RevealOut
from app.api.deps import require_role

router = APIRouter(prefix="/fairness", tags=["Fairness"])

@router.get("/odds/{case_id}/{version}")
async def get_odds(case_id: str, version: str):
    """
    Повернути або перенаправити на JSON з шансами.
    """
    # url = f"{settings.s3_base_url}/odds/{case_id}/{version}.json"
    # # опціонально можна перевірити існування ключа в S3
    # return RedirectResponse(url)


@router.post("/commit", response_model=CommitOut)
async def commit_seed(user=Depends(require_role("user")))-> CommitOut:
    
    not_used_seed = await ServerSeed.find_one({"user_id": str(user.user_id), "used": False})
    if not not_used_seed:
    # generate new seed
        raw = os.urandom(32)
        hex_seed = raw.hex()
        hash_digest = hashlib.sha256(raw).hexdigest()
        
        # save seed to DB
        server_seed =  ServerSeed(
            seed=hex_seed,
            hash=hash_digest,
            owner_id=str(user.user_id)
            )
        await server_seed.insert()
        server_seed = str(server_seed.id)
    else:
        server_seed = str(not_used_seed.id)
        hash_digest = not_used_seed.hash
    #return the hash, document id
    return CommitOut(
        server_seed_id=server_seed,
        hash=hash_digest,

        )
    
@router.get(
    "/reveal/{spin_log_id}",
    response_model=RevealOut,
    summary="Reveal server seed for a specific spin",
    description=(
        "Returns the server_seed, table_id and odds_version for a provably-fair spin. "
        "Requires the spin_log_id returned by /cases/open and valid authentication."
    ),
)
async def reveal_pf(
    spin_log_id: PydanticObjectId = Path(
        ..., description="Identifier of the spin log entry to reveal"
    ),
    user=Depends(require_role("user"))
) -> RevealOut:
    # 1. Retrieve the spin log and verify ownership
    spin = await SpinLog.get(spin_log_id)
    if not spin:
        raise HTTPException(status_code=404, detail="spin_log_not_found")
    if spin.user_id != user.id:
        raise HTTPException(status_code=403, detail="forbidden")

    # 2. Retrieve the committed server seed document
    seed_doc = await ServerSeed.get(spin.server_seed_id)
    if not seed_doc:
        raise HTTPException(status_code=404, detail="server_seed_not_found")

    # 3. Optional integrity check
    import hashlib
    expected_hash = hashlib.sha256(bytes.fromhex(seed_doc.seed)).hexdigest()
    if expected_hash != seed_doc.hash:
        raise HTTPException(status_code=500, detail="server_seed_hash_mismatch")

    # 4. Return the reveal payload
    return RevealOut(
        server_seed=seed_doc.seed,
        table_id=spin.table_id,
        odds_version=spin.odds_version or spin.table_id
    )