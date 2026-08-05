from pydantic import BaseModel, EmailStr


class SessionCreateDTO(BaseModel):
    email: EmailStr
    password: str
    user_agent: str
    user_ip: str | None
    device_type: str = "other"
