from fastapi import APIRouter

from src.api.system import router as system_router
from src.api.v1.router import router as v1_router

router = APIRouter(prefix="/api")

router.include_router(system_router)
router.include_router(v1_router)
