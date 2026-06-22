from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.core.config import settings
from backend.app.core.exceptions import register_exception_handlers
from backend.app.middleware.supabase_auth import supabase_auth_middleware


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.API_VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(supabase_auth_middleware)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
