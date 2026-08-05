from pydantic import BaseModel, EmailStr


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
