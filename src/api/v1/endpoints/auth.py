import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Request, Response, status

from src.api.v1.schemas.auth import (
    GetSaltResponseSchema,
    LoginForm,
    LoginResponse,
    RegisterForm,
)

# from src.api.v1.depends import CurrentUserDep
from src.domain.exceptions import PasswordsNotMatch
from src.services.user import IUserService

# from src.domain.dtos.address import AddressCreateDTO, AddressUpdateDTO

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    route_class=DishkaRoute
)


@router.get(
    "/salt",
    summary="Get the user salt.",
    response_model=GetSaltResponseSchema,
)
async def get_salt(
    email: str,
    user_service: FromDishka[IUserService],
):
    user_salt = await user_service.get_salt_by_email(email)
    return GetSaltResponseSchema(**user_salt.model_dump())


@router.post(
    "/register/",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    register_form: RegisterForm,
    request: Request,
    response: Response,
    auth_service: AuthDep,
    jwt_service: JWTDep,
    session_service: SessionDep,
) -> LoginResponse:
    if register_form.password != register_form.confirm_password:
        raise PasswordsNotMatch
    user = await auth_service.registration_new_user(
        register_form.username, register_form.email,
        register_form.password
    )
    access_token = jwt_service.generate_access_token(user)
    refresh_token = jwt_service.generate_refresh_token(user)
    session = SessionFactory.create(
        user_id=user.id,
        jti=jwt_service.jti,
        user_agent=request.headers["user-agent"],
        refresh_token=refresh_token,
        user_ip=request.headers["host"],
    )
    await session_service.create_new_session(session=session)
    set_refresh_token(response=response, refresh_token=refresh_token)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/login/",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
)
async def login(
    request: Request,
    response: Response,
    login_form: LoginForm,
    auth_service: AuthDep,
    jwt_service: JWTDep,
    session_service: SessionDep,
) -> LoginResponse:
    user = await auth_service.login_user(
        email=login_form.email, password=login_form.password
    )
    access_token = jwt_service.generate_access_token(user)
    refresh_token = jwt_service.generate_refresh_token(user)
    session = SessionFactory.create(
        user_id=user.id,
        jti=jwt_service.jti,
        user_agent=request.headers["user-agent"],
        refresh_token=refresh_token,
        user_ip=request.headers["host"],
    )
    await session_service.create_new_session(session=session)
    set_refresh_token(response=response, refresh_token=refresh_token)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    session_service: SessionDep,
    blacklist_service: BlacklistDep,
    refresh_token: str = Depends(get_refresh_token),
):
    deactivate_session = await session_service.deactivate_current_session(refresh_token)
    await blacklist_service.set_one_value(
        deactivate_session.jti,
        deactivate_session.user_id,
        settings.service.access_token_expire,
    )
    return


@router.post(
    "/refresh/", response_model=LoginResponse, status_code=status.HTTP_200_OK
)
async def refresh(
    response: Response,
    session_service: SessionDep,
    jwt_service: JWTDep,
    refresh_token: str = Depends(get_refresh_token),
    current_user: User = Depends(get_current_user),
) -> LoginResponse:
    new_refresh_token = jwt_service.generate_refresh_token(user=current_user)
    new_access_token = jwt_service.generate_access_token(user=current_user)
    new_jti = jwt_service.jti
    _ = await session_service.update_session_refresh_token(
        refresh_token, new_refresh_token, new_jti
    )
    set_refresh_token(response=response, refresh_token=new_refresh_token)
    return LoginResponse(access_token=new_access_token, refresh_token=new_refresh_token)

# @router.get(
#     "/{address_id}",
#     summary="Получить данные об адресе",
#     response_model=AddressResponseSchema,
# )
# async def get_address(
#     address_service: FromDishka[IAddressService], address_id: UUID, user: CurrentUserDep
# ):
#     address = await address_service.get_address_by_id(
#         address_id=address_id, user_id=user.id
#     )
#     return AddressResponseSchema(**address.model_dump())
