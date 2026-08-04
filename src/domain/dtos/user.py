from uuid import UUID

from pydantic import BaseModel, Field


class UserCreateDTO(BaseModel):
    user_id: UUID
    latitude: float
    longitude: float
    country: str
    city: str
    street: str
    house: str
    flat: str | None = Field(default=None)
