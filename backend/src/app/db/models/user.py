from beanie import Document, Indexed
from pydantic import BaseModel, Field
from typing import List, Optional, ClassVar, Dict
from datetime import datetime, timezone


class User(Document):
    SCHEMA_VERSION: ClassVar[float] = 1.0
    
    user_id: int = Indexed(unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    wallets: Dict[str, Dict[str, str]] = Field(default_factory=Dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    history: List[str] = Field(default_factory=list)
    schema_version: float = Field(default=SCHEMA_VERSION)

    class Settings:
        name = "users"