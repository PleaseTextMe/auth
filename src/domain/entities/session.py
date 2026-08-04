from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Session(BaseModel):
    id: UUID | None
    user_id: int
    user_agent: str
    jti: UUID
    refresh_token: str
    user_ip: str | None
    is_active: bool
    device_type: str = "other"
    created_at: datetime | None = None
    updated_at: datetime | None = None
