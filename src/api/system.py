from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/health")
async def healthcheck():
    return {"status": "ok"}


прочти если аксель