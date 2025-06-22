# src/app/models/status_history.py

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class StatusHistoryEntry(BaseModel):
    status: str                           # новий поточний статус після зміни
    changed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: Optional[str] = None        # наприклад, user_id (гравця чи адміна)
    actor_role: Optional[str] = None      # "user" | "admin" | "system" | "service"
    reason: Optional[str] = None          # якщо status="rejected" (або інша причина)
    ip_address: Optional[str] = None      # звідки був запит (IP-адреса)
    user_agent: Optional[str] = None      # User Agent (браузер/сервер)
    country: Optional[str] = None         # ISO-код країни або опис локації

    class Config:
        json_schema_extra = {
            "example": {
                "status": "pending_internal",
                "changed_at": "2025-06-03T12:34:56.000Z",
                "actor_id": "user_123",
                "actor_role": "user",
                "reason": None,
                "ip_address": "192.0.2.1",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)…",
                "country": "UA"
            }
        }
