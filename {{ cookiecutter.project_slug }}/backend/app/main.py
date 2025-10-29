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
            # Mask sensitive values
            if any(secret in key.lower() for secret in ["password", "key", "secret", "token"]):
                logger.info(f"{key}: ******")
            else:
                logger.info(f"{key}: {value}")

    {% if cookiecutter.use_postgres == 'y' %}
    # Initialize database connection
    try:
        from app.core.database import check_db_connection, init_db
        
        if check_db_connection():
            logger.info("Database connection successful")
            # Uncomment to auto-create tables (use Alembic in production)
            # init_db()
        else:
            logger.warning("Database connection failed - some features may not work")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
    
    {% endif %}
    # TODO: Add additional application startup logic

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

# Include middleware (order matters - first added is outermost)
from app.core.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
)

# Security headers (outermost)
app.add_middleware(SecurityHeadersMiddleware)

# Request logging
app.add_middleware(RequestLoggingMiddleware)

# Rate limiting (optional, uncomment to enable)
# app.add_middleware(RateLimitMiddleware)

# Error handling
app.add_middleware(ErrorHandlingMiddleware)

# CORS middleware
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
from app.routers.api.v1.health import router as health_router

# Health checks for infrastructure
app.include_router(health_router)

# API routes (versioned)
app.include_router(main_router)

@app.get("/")
async def root():
    logger.info("Root endpoint called")

    if not settings.is_production:
        return RedirectResponse(url="/docs", status_code=307)

    return JSONResponse(content={"title": "{{ cookiecutter.project_name }}", "status": "ok"}, status_code=200)
