from pydantic import BaseModel


class Permission(BaseModel):
    slug: str
    description: str
