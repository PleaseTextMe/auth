import re
from pydantic import BaseModel, EmailStr, field_validator


class PublicBundleSchema(BaseModel):
    bundle_json: str
    signature: str


class VaultSchema(BaseModel):
    encrypted_payload: str
    nonce: str
    auth_tag: str


class LoginForm(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_chars(cls, v: str) -> str:
        # Ensures the password contains only basic printable ASCII characters (e.g., no Cyrillic, emojis, or special unicode)
        # This prevents encoding issues across different platforms/browsers (like Safari).
        if not re.match(r'^[\x20-\x7E]+$', v):
            raise ValueError("password must contain only basic ascii characters (no cyrillic or special unicode)")
        return v


class RegisterForm(LoginForm):
    username: str
    verify_token: str
    public_bundle: PublicBundleSchema
    vault: VaultSchema


class SendCodeForm(BaseModel):
    email: EmailStr


class CheckCodeForm(BaseModel):
    email: EmailStr
    code: int
    verify_token: str


class LoginResponse(BaseModel):
    auth_token: str


class SendCodeResponse(BaseModel):
    verify_token: str


class CheckVerifyCodeResponse(BaseModel):
    is_verified: bool
