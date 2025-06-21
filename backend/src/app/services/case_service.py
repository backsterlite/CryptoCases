import random
import json

from decimal import Decimal
from typing import Dict, Mapping, Any
from pathlib import Path
from datetime import datetime, timezone

from fastapi import HTTPException,  status

from app.db.models.user import User
from app.services.wallet_service import  WalletService
from app.db.models.case_log import CaseLog
from app.services.odds_service import export_odds
from app.core.config.settings import get_settings
from app.core.config.start_cases_config import START_CASES
from app.db.models.case_config import CaseConfig, TierConfig, RewardItem, OddsVersion


class CaseService:
    _settings = get_settings()
    
    @staticmethod
    def get_odds_table(case_id: str, version: str) -> str:
        tablePath = Path(f"{CaseService._settings.project_root_path}/data/odds/{case_id}/reward_table_{case_id}_{version}.json")
        with open(file=tablePath, mode="r") as table_json:
            table_data = json.load(table_json, parse_float=Decimal)
        
        return table_data

    @staticmethod
    async def init_cases():
        now = datetime.now(timezone.utc).isoformat()
        odds_version = OddsVersion(version=now)
        for case in START_CASES:
            new_case = CaseConfig(
                case_id=case["case_id"],
                price_usd=case["price_usd"],
                tiers=[
                    TierConfig(
                        name=tier["name"],
                        chance=tier["chance"],
                        rewards=[
                            RewardItem(
                                coin_id=reward["coin_amount"]["coin"]["id"],
                                amount=reward["coin_amount"]["amount"],
                                network=reward["coin_amount"]["network"],
                                sub_chance=reward["sub_chance"]
                            )
                            for reward in tier["rewards"]
                        ]
                    )
                    for tier in case["tiers"]
                    ],
                pity_after=case["pity_after"],
                pity_bonus_tier=case["pity_bonus_tier"],
                global_pool_usd=Decimal(case["global_pool_usd"]),
                pool_reset_interval=case["pool_reset_interval"],
                odds_versions=[odds_version]
            )
            await new_case.insert()
            await export_odds(new_case.case_id, to_bucket=False)
            
    @staticmethod
    async def check_cases_init():
        return await CaseConfig.find_all().count() >= 3

    @staticmethod
    async def get_all_cases():
        return await CaseConfig.find_all().to_list()
    
    @staticmethod
    async def get_case_by_id(case_id: str):
        current_case = await CaseConfig.find_one(CaseConfig.case_id==case_id)
        if not current_case:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "case id mismatched")
        nonce = random.randint(1, 100)
        case_data: Dict[str,Any] = current_case.model_dump()
        return {**case_data, "nonce": nonce}