from pydantic import BaseModel


class UserResponse(BaseModel):
    username: str
    public_bundle: dict
