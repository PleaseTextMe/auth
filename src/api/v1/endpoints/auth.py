import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, status

from src.api.v1.depends import CurrentSessionDep, CurrentUserDep
from src.api.v1.schemas.auth import (
    CheckCodeForm,
    CheckVerifyCodeResponse,
    LoginForm,
    LoginResponse,
    RegisterForm,
    SendCodeForm,
    SendCodeResponse,
)
from src.domain.dtos.session import SessionCreateDTO
from src.domain.dtos.user import UserCreateDTO
from src.domain.dtos.verify import VerifyCodeDTO
from src.services.session import ISessionService
from src.services.user import IUserService
from src.services.verify import IVerifyService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=DishkaRoute)


@router.post(
    "/register/",
    summary="Регистрация нового пользователя.",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: Request,
    register_form: RegisterForm,
    user_service: FromDishka[IUserService],
    session_service: FromDishka[ISessionService],
) -> LoginResponse:
    await user_service.create(UserCreateDTO(**register_form.model_dump()))
    auth_token = await session_service.create(
        SessionCreateDTO(
            **register_form.model_dump(),
            user_agent=request.headers["user-agent"],
            user_ip=request.headers["host"],
        )
    )
    return LoginResponse(auth_token=auth_token)


@router.post(
    "/login/",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: Request,
    login_form: LoginForm,
    session_service: FromDishka[ISessionService],
) -> LoginResponse:
    auth_token = await session_service.create(
        SessionCreateDTO(
            **login_form.model_dump(),
            user_agent=request.headers["user-agent"],
            user_ip=request.headers["host"],
        )
    )
    return LoginResponse(auth_token=auth_token)


@router.post(
    "/send-verify-code/",
    response_model=SendCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def send_verify_code(
    send_code_form: SendCodeForm,
    verify_service: FromDishka[IVerifyService],
) -> SendCodeResponse:
    verify_token = await verify_service.create_email_code(send_code_form.email)
    return SendCodeResponse(verify_token=verify_token)


@router.post(
    "/check-verify-code/",
    response_model=CheckVerifyCodeResponse,
    status_code=status.HTTP_200_OK,
)
async def check_verify_code(
    check_code_form: CheckCodeForm,
    verify_service: FromDishka[IVerifyService],
) -> CheckVerifyCodeResponse:
    await verify_service.verify_email_code(VerifyCodeDTO(**check_code_form.model_dump()))
    return CheckVerifyCodeResponse(is_verified=True)


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(session_service: FromDishka[ISessionService], session: CurrentSessionDep):
    await session_service.logout(session.auth_token_hash)


@router.get("/me/")
async def get_me(user: CurrentUserDep):
    return user


@router.get("/my-session/")
async def get_my_session_info(session: CurrentSessionDep):
    return session
