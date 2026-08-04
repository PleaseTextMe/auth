from datetime import datetime

from pydantic import BaseModel, Field

from src.core.utils.datetime import get_utc_now


class DateTimeMixin(BaseModel):
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)

    def touch(self) -> None:
        self.updated_at = get_utc_now()
