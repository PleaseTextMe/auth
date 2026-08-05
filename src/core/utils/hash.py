import hashlib

from argon2 import PasswordHasher

password_hasher = PasswordHasher()


def hash_token(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()
