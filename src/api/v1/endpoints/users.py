import logging

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.services.user import IUserService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    route_class=DishkaRoute
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    user_service: FromDishka[IUserService],
) -> list[dict]:
    users = await user_service.get_all()
    return [{"username": u.username, "public_bundle": u.public_bundle} for u in users]
