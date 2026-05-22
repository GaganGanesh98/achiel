from app.api.admin_domains import admin_router as admin_domains_router
from app.api.auth import router as auth_router
from app.api.comments import router as comments_router
from app.api.posts import router as posts_router
from app.api.reports import admin_router as admin_reports_router
from app.api.reports import router as reports_router
from app.api.universities import router as universities_router

__all__ = [
    "admin_domains_router",
    "auth_router",
    "comments_router",
    "posts_router",
    "universities_router",
    "reports_router",
    "admin_reports_router",
]
