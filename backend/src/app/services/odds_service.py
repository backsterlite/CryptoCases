# services/odds_service.py
import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from app.db.models.case_config import CaseConfig
from app.config.settings import settings
import aioboto3

async def export_odds(case_id: str, to_bucket: bool = True) -> Path:
    """
    Generate JSON with odds.
    If to_bucket=True, upload to S3; otherwise, save locally.
    Returns the URL or file path.
    """
    # Fetch case configuration from database
    cfg = await CaseConfig.find_one(CaseConfig.case_id == case_id)
    if not cfg:
        raise ValueError(f"CaseConfig {case_id} not found")

    # Build payload structure
    payload = {
        "case_id": cfg.case_id,
        "version": cfg.odds_versions[-1].version,
        "tiers": [
            {
                "name": tier.name,
                "chance": tier.chance,
                "rewards": [
                    {
                        "coin_id": r.coin_id,
                        "network": r.network,
                        "amount": r.amount,
                        "sub_chance": r.sub_chance,
                    }
                    for r in tier.rewards
                ],
            }
            for tier in cfg.tiers
        ],
    }
    body = json.dumps(payload, indent=2, default=str, ensure_ascii=False).encode()
    # key = f"odds/{case_id}/{cfg.odds_versions[-1]}.json"

    if to_bucket:
        # Upload JSON to S3 bucket
        # session = aioboto3.Session()
        # async with session.client(
        #     "s3",
        #     aws_access_key_id=settings.aws_key,
        #     aws_secret_access_key=settings.aws_secret
        # ) as s3:
        #     await s3.put_object(Bucket=settings.s3_bucket, Key=key, Body=body)
        # # Return the public URL
        # return f"{settings.s3_base_url}/{key}"
        pass
    else:
        # Save JSON locally under configured directory
        local_dir = settings.local_odds_dir  # e.g. "./data/odds"
        os.makedirs(Path(local_dir, case_id), exist_ok=True)
        path = Path(local_dir, case_id, f"{cfg.odds_versions[-1].version}.json")
        with open(path, "wb") as f:
            f.write(body)
        # Return the local file system path
        file_sha256_sum = get_file_hash_sum(path)
        cfg.odds_versions[-1].sha256 = file_sha256_sum
        await cfg.save()
        return path

def get_file_hash_sum(file_path: Path) -> str:
    file_hash = hashlib.sha256()
    with open(file=file_path, mode="rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            file_hash.update(chunk)
    return file_hash.hexdigest()

async def get_odds_table_path(case_id: str, odds_version: str) -> Path:
    return settings.local_odds_dir / case_id / f"{odds_version}.json"