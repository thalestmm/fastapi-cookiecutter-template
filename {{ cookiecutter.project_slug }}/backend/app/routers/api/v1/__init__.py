from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["v1"])

__all__ = ["router"]