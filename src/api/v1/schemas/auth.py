from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class PublicBundleSchema(BaseModel):
    bundle_json: str
    signature: str


class VaultSchema(BaseModel):
    encrypted_payload: str
    nonce: str
    auth_tag: str
    kdf_salt: str | None = None
    auth_version: Literal[1, 2] = 1


class LoginParametersForm(BaseModel):
    email: EmailStr


class LoginForm(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class RegisterForm(LoginForm):
    username: str = Field(min_length=1, max_length=32)
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
