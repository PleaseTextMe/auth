from pydantic import BaseModel, ConfigDict, Field

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.mixins import DateTimeMixin


class Session(DateTimeMixin, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user_agent: str
    auth_token_hash: bytes = Field(exclude=True, repr=False)
    user_ip: str | None
    is_active: bool
    device_type: str

    @classmethod
    def create(
        cls,
        user_id: int,
        user_agent: str,
        auth_token_hash: bytes,
        user_ip: str | None,
        is_active: bool = True,
        device_type: str = "other",
        **kwargs,
    ) -> "Session":
        return cls(
            id=generate_snowflake_id(),
            user_id=user_id,
            user_agent=user_agent,
            auth_token_hash=auth_token_hash,
            user_ip=user_ip,
            is_active=is_active,
            device_type=device_type,
        )
