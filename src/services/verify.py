import json
import logging
import secrets
from abc import ABC, abstractmethod

from pydantic import EmailStr

from src.core.metrics import AUTH_CODES_GENERATED, AUTH_EMAIL_VERIFICATIONS
from src.domain.dtos.verify import VerifyCodeDTO
from src.domain.exceptions import (
    CodeHasExpired,
    InvalidVerifyCode,
    UserEmailAlreadyExists,
)
from src.infrastructure.email import send_verification_email
from src.services.interfaces.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class IVerifyService(ABC):

    @abstractmethod
    async def create_email_code(self, user_email: EmailStr) -> str: ...

    @abstractmethod
    async def verify_email_code(self, verify_data: VerifyCodeDTO): ...


class VerifyService(IVerifyService):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def create_email_code(self, user_email: EmailStr) -> str | None:
        async with self._uow as uow:
            if await uow.user_repository.get_by_email(user_email=user_email):
                raise UserEmailAlreadyExists()
            verification_code = 100_000 + secrets.randbelow(900_000)
            verify_token = secrets.token_urlsafe(32)

            redis_data = {
                "email": user_email,
                "code": verification_code,
                "status": "pending"
            }

            await uow.verify_repository.set_value(
                key=verify_token,
                value=json.dumps(redis_data),
                exp=5
            )
            try:
                await send_verification_email(user_email, verification_code)
            except Exception:
                await uow.verify_repository.delete_value(verify_token)
                raise

            AUTH_CODES_GENERATED.inc()
            return verify_token

    async def verify_email_code(self, verify_data: VerifyCodeDTO):
        async with self._uow as uow:
            if await uow.user_repository.get_by_email(
                user_email=verify_data.email
            ):
                AUTH_EMAIL_VERIFICATIONS.labels(status="failed").inc()
                raise UserEmailAlreadyExists()

            result = await uow.verify_repository.verify_code(
                verify_data.verify_token, str(verify_data.email), verify_data.code
            )
            if result == -1:
                AUTH_EMAIL_VERIFICATIONS.labels(status="failed").inc()
                raise CodeHasExpired()

            if result != 1:
                AUTH_EMAIL_VERIFICATIONS.labels(status="failed").inc()
                raise InvalidVerifyCode()

            AUTH_EMAIL_VERIFICATIONS.labels(status="success").inc()
