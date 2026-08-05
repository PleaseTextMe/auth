from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.mixins import DateTimeMixin


class User(DateTimeMixin, BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(default_factory=generate_snowflake_id)
    username: str
    email: EmailStr
    password_hash: bytes = Field(exclude=True, repr=False)
    public_bundle: dict
    vault: dict
    is_active: bool

    @classmethod
    def create(
        cls,
        username: str,
        email: EmailStr,
        password_hash: str,
        public_bundle: dict,
        vault: dict,
        is_active: bool = True,
        **kwargs,
    ) -> "User":
        return cls(
            id=generate_snowflake_id(),
            username=username,
            email=email,
            password_hash=password_hash,
            public_bundle=public_bundle,
            vault=vault,
            is_active=is_active,
        )
