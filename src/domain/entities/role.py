from pydantic import BaseModel, Field

from src.domain.entities.permission import Permission


class Role(BaseModel):
    slug: str
    title: str
    description: str
    permissions: list[Permission] = Field(default_factory=list)
