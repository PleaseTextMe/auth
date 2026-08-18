from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.v1.router import router
from src.infrastructure.container import Container
from src.infrastructure.handlers.exceptions import exception_handlers
from src.infrastructure.lifetime import AppLifetime


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    app_lifetime = AppLifetime()
    await app_lifetime.startup()
    try:
        yield
    finally:
        await app_lifetime.shutdown()
        await fastapi_app.state.dishka_container.close()


import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

def create_app() -> FastAPI:
    fastapi_app = FastAPI(
        lifespan=lifespan,
        docs_url="/api/openapi",
        openapi_url="/api/openapi.json",
        exception_handlers=exception_handlers
    )

    @fastapi_app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "traceback": traceback.format_exc()}
        )

    fastapi_app.include_router(router, prefix="/api")
    container = make_async_container(Container())
    setup_dishka(container=container, app=fastapi_app)
    Instrumentator().instrument(fastapi_app).expose(fastapi_app)
    return fastapi_app


app = create_app()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    app()
