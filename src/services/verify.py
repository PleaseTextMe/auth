import json
import logging
import secrets
from abc import ABC, abstractmethod

from pydantic import EmailStr

from src.domain.dtos.verify import VerifyCodeDTO
from src.domain.exceptions import (
    CodeHasExpired,
    InvalidVerifyCode,
    UserEmailAlreadyExists,
)
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
            # verification_code = int(f"{secrets.randbelow(1000000):06d}")  TODO: Restore this
            verification_code = 666_666
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

            return verify_token

    async def verify_email_code(self, verify_data: VerifyCodeDTO):
        async with self._uow as uow:
            if await uow.user_repository.get_by_email(
                user_email=verify_data.email
            ):
                raise UserEmailAlreadyExists()

            raw_redis_data = await uow.verify_repository.get_value(
                verify_data.verify_token
            )
            if not raw_redis_data:
                raise CodeHasExpired()

            redis_data = json.loads(raw_redis_data)
            if not(
                redis_data["email"] == verify_data.email
                and redis_data["code"] == verify_data.code
            ):
                raise InvalidVerifyCode()

            await uow.verify_repository.update_field(
                key=verify_data.verify_token, 
                field="status", 
                value="verified",
                new_exp=24 * 60
            )
