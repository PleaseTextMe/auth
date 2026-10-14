from pydantic import BaseModel, EmailStr


class PublicBundleDTO(BaseModel):
    bundle_json: str
    signature: str


class VaultDTO(BaseModel):
    encrypted_payload: str
    nonce: str
    auth_tag: str
    kdf_salt: str | None = None
    auth_version: int = 1


class UserCreateDTO(BaseModel):
    username: str
    email: EmailStr
    password: str
    verify_token: str
    public_bundle: PublicBundleDTO
    vault: VaultDTO


class UserCreateDatabaseDTO(BaseModel):
    username: str
    email: EmailStr
    password_hash: bytes
    public_bundle: dict
    vault: dict
