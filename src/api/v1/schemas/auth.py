from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, EmailStr, Field


class LoginForm(BaseModel):
    email: Annotated[EmailStr, Form(...)]
    password: Annotated[str, Form(...)]


class RegisterForm(LoginForm):
    username: Annotated[str, Form(...)]


class GetSaltResponseSchema(BaseModel):
    kdf_salt: str


class LoginResponse(BaseModel):
    refresh_token: str
    access_token: str
    token_type: str = Field(default="jwt")
