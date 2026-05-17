from app.api.auth import router as auth_router
from app.api.posts import router as posts_router
from app.api.universities import router as universities_router

__all__ = ["auth_router", "posts_router", "universities_router"]
