from pydantic import BaseModel


class Token(BaseModel):
    user_id: int
    iat: str
    exp: str
    jti: str
    scope: list[str]
