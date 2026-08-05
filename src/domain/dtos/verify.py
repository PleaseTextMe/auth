from pydantic import BaseModel, EmailStr


class VerifyCodeDTO(BaseModel):
    email: EmailStr
    code: int
    verify_token: str
