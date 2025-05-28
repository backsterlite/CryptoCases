from beanie import Document, Indexed
from pydantic import Field
from typing import Optional, ClassVar
from datetime import datetime, timezone


class User(Document):
    SCHEMA_VERSION: ClassVar[float] = 1.0
    
    user_id: int = Indexed(unique=True)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_name: Optional[str] = None
    photo_url: Optional[str] = None
    role: str = Field(default="user", description="Роль: user | admin | worker")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: float = Field(default=SCHEMA_VERSION)

    class Settings:
        name = "users"