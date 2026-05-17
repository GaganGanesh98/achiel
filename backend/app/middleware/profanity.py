from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class ProfanityGuardMiddleware(BaseHTTPMiddleware):
    """
    Reserved layer for request-wide checks. Post and comment bodies are censored
    in routers via `app.services.moderation.check_and_clean`.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        return await call_next(request)
