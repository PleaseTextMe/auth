from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.core.utils.snowflake import generate_snowflake_id
from src.domain.entities.mixins import DateTimeMixin


class User(DateTimeMixin, BaseModel):
    id: int = Field(default_factory=generate_snowflake_id)
    username: str
    email: EmailStr
    auth_hash: str
    is_active: bool
    roles: list = Field(default_factory=list)
    kdf_salt: str

    @classmethod
    def create(
        cls,
        username: str,
        email: EmailStr,
        auth_hash: str,
        is_active: bool,
        roles: list,
        kdf_salt: str,
    ) -> "User":
        return cls(
            id=generate_snowflake_id(),
            username=username,
            email=email,
            auth_hash=auth_hash,
            is_active=is_active,
            roles=roles,
            kdf_salt=kdf_salt,
        )


class UserSalt(BaseModel):
    kdf_salt: str

    model_config = ConfigDict(from_attributes=True)
