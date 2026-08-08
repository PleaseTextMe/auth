from fastapi import APIRouter

from src.api.v1.endpoints.auth import router as auth_router
from src.api.v1.endpoints.users import router as users_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(users_router)

