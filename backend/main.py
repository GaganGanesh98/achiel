from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.university_email import load_disposable_domains
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api import (
    admin_domains_router,
    admin_reports_router,
    auth_router,
    comments_router,
    posts_router,
    reports_router,
    universities_router,
)
from app.core.config import settings
from app.core.limiter import limiter
from app.middleware.profanity import ProfanityGuardMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_disposable_domains()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="CampusVoice API", lifespan=lifespan)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ProfanityGuardMiddleware)

    app.include_router(auth_router)
    app.include_router(posts_router)
    app.include_router(comments_router)
    app.include_router(universities_router)
    app.include_router(reports_router)
    app.include_router(admin_reports_router)
    app.include_router(admin_domains_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
