from beanie import Document
from pydantic import Field
from datetime import datetime, timezone

class CaseLog(Document):
    user_id: str
    case_id: str
    token: str
    network: str
    amount: str  # stringified Decimal
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    class Settings:
        name = "case_logs"
