"""
The routers module contains the FastAPI routers for the application.
"""

from fastapi import APIRouter
from app.routers.api import router as api_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(api_router)

__all__ = ["router"]