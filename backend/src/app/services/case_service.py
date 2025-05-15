import random
import json

from decimal import Decimal
from typing import Dict
from pathlib import Path

from app.db.models.user import User
from app.services.wallet_service import has_sufficient_balance, WalletService
from app.db.models.case_log import CaseLog
from app.config.settings import settings


    
def get_odds_table(case_id: str, version: str) -> str:
    tablePath = Path(f"{settings.project_root_path}/data/odds/{case_id}/reward_table_{case_id}_{version}.json")
    with open(file=tablePath, mode="r") as table_json:
        table_data = json.load(table_json, parse_float=Decimal)
    
    return table_data