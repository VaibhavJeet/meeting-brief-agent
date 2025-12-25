"""API routes."""

from app.api.meetings import router as meetings_router
from app.api.briefs import router as briefs_router
from app.api.contacts import router as contacts_router
from app.api.settings import router as settings_router

__all__ = [
    "meetings_router",
    "briefs_router",
    "contacts_router",
    "settings_router",
]
