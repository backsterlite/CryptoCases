
import hashlib

from beanie import PydanticObjectId
from pymongo import ReturnDocument
from fastapi import HTTPException

from app.db.models.player import ServerSeed


class FairnessService:
    
    @classmethod
    async def reveal_and_verify(cls, commit_id: PydanticObjectId, user_id: int):
        """
        1. Atomically find and mark seed as used
        2. Verify that it belongs to this user
        3. Return a document with seed and hash fields
        """
        raw = await ServerSeed.get_motor_collection().find_one_and_update(
            {
                "_id": commit_id,
                "owner_id": str(user_id),
                "used": False,
            },
            {"$set": {"used": True}},
            return_document=ReturnDocument.AFTER,
        )
        
        if not raw:
            raise HTTPException(
                status_code=400,
                detail="invalid or already used commit_id",
            )
        seed_doc = ServerSeed.model_validate(raw)
        # Integrity check (опціонально, але корисно для тестів)
        expected_hash = hashlib.sha256(bytes.fromhex(seed_doc.seed)).hexdigest()
        if expected_hash != seed_doc.hash:
            # тут можна зробити логгер і alert
            raise HTTPException(
                status_code=500,
                detail="server_seed hash mismatch",
            )

        return seed_doc