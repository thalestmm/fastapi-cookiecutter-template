"""
Main FastAPI application entrypoint for {{ cookiecutter.project_name }}
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging_config import setup_logging

# Configure logging with file output
logger = setup_logging(
    log_level = settings.LOG_LEVEL,
    log_file_path=str(settings.LOG_DIR / "backend.log"),
    service_name="{{ cookiecutter.project_slug }}",
    max_bytes=settings.LOG_FILE_MAX_BYTES,
    backup_count=settings.LOG_FILE_BACKUP_COUNT
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI application lifespan manager.

    Handles startup and shutdown events.
    """
    logger.info("=" * 80)
    logger.info("Starting up application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 80)

    if settings.ENVIRONMENT == "development":
        logger.info("Environment variables:")
        for key, value in settings.model_dump().items():
            logger.info(f"{key}: {value}")

    # TODO: Add the the application startup logic

    logger.info("=" * 80)
    logger.info("Application startup complete")
    logger.info("=" * 80)

    yield

    # TODO: Add the application shutdown logic

    logger.info("Shutting down application...")
    logger.info("=" * 80)

# Main application entrypoint
app: FastAPI = FastAPI(
    title="{{ cookiecutter.project_name }}",
    version="0.0.0",
    description="{{ cookiecutter.project_description }}",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
    contact={
        "name": "{{ cookiecutter.author }}",
        "email": "{{ cookiecutter.email }}",
    }
)

# Include CORS middleware
app.add_middleware(
    CORSMiddleware,
    # TODO: Adjust CORS origins for production
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup routes from all the routers
from app.routers import router as main_router

app.include_router(main_router)

@app.get("/")
async def root():
    logger.info("Root endpoint called")

    if not settings.is_production:
        return RedirectResponse(url="/docs", status_code=307)

    return JSONResponse(content={"title": "{{ cookiecutter.project_name }}", "status": "ok"}, status_code=200)
