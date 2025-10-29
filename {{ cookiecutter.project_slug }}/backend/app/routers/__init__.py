from app.routers.api import router as api_router

router = APIRouter(prefix="/api", tags=["api"])

router.include_router(api_router)

__all__ = ["router"]