"""
Health check endpoints for monitoring application status.
"""
from datetime import datetime
import sys
from fastapi import APIRouter, status

from app.core.config import settings
from app.schemas.api.v1.health import HealthResponse, DetailedHealthResponse
{% if cookiecutter.use_postgres == 'y' %}
from app.core.database import check_db_connection
{% endif %}
{% if cookiecutter.use_celery == 'y' %}
from app.worker.client import get_worker_stats
{% endif %}
{% if cookiecutter.use_celery == 'y' %}
from app.core.redis import get_redis_connection
import redis
{% endif %}

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns basic information about the application status.
    This endpoint should respond quickly and is suitable for
    load balancer health checks.
    
    Returns:
        HealthResponse: Basic health information
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.0.0",  # TODO: Load from package version
        environment=settings.ENVIRONMENT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )


@router.get("/live", response_model=HealthResponse)
async def liveness_check() -> HealthResponse:
    """
    Kubernetes liveness probe endpoint.
    
    Indicates whether the application is running.
    If this fails, the container should be restarted.
    
    Returns:
        HealthResponse: Liveness status
    """
    return HealthResponse(
        status="alive",
        timestamp=datetime.utcnow(),
        version="0.0.0",
        environment=settings.ENVIRONMENT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )


@router.get("/ready", response_model=DetailedHealthResponse)
async def readiness_check() -> DetailedHealthResponse:
    """
    Kubernetes readiness probe endpoint.
    
    Indicates whether the application is ready to serve traffic.
    Checks dependencies like Redis, Celery workers, etc.
    
    Returns:
        DetailedHealthResponse: Readiness status with service checks
    """
    services_status = {}
    overall_status = "ready"
    
    {% if cookiecutter.use_postgres == 'y' %}
    # Check PostgreSQL database
    try:
        if check_db_connection():
            services_status["database"] = {"status": "healthy", "type": "postgresql"}
        else:
            services_status["database"] = {"status": "unhealthy", "type": "postgresql"}
            overall_status = "not_ready"
    except Exception as e:
        services_status["database"] = {
            "status": "unhealthy",
            "type": "postgresql",
            "error": str(e)
        }
        overall_status = "not_ready"
    
    {% endif %}
    {% if cookiecutter.use_celery == 'y' %}
    # Check Redis
    try:
        redis_conn = get_redis_connection()
        redis_conn.ping()
        services_status["redis"] = {"status": "healthy"}
    except (redis.ConnectionError, Exception) as e:
        services_status["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_status = "not_ready"
    
    # Check Celery workers
    try:
        worker_stats = get_worker_stats()
        worker_count = len(worker_stats.get("worker_stats", {}))
        if worker_count > 0:
            services_status["celery"] = {
                "status": "healthy",
                "workers": worker_count
            }
        else:
            services_status["celery"] = {
                "status": "unhealthy",
                "workers": 0,
                "error": "No workers available"
            }
            overall_status = "not_ready"
    except Exception as e:
        services_status["celery"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "not_ready"
    {% endif %}
    
    {% if cookiecutter.use_supabase == 'y' %}
    # Check Supabase connection
    try:
        from app.core.supabase import get_supabase_client
        supabase = get_supabase_client()
        # Simple check - if client was created, assume healthy
        services_status["supabase"] = {"status": "healthy"}
    except Exception as e:
        services_status["supabase"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "not_ready"
    {% endif %}
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="0.0.0",
        environment=settings.ENVIRONMENT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        services=services_status
    )


@router.get("/startup", response_model=HealthResponse)
async def startup_check() -> HealthResponse:
    """
    Kubernetes startup probe endpoint.
    
    Indicates whether the application has finished starting up.
    Use this for slow-starting applications.
    
    Returns:
        HealthResponse: Startup status
    """
    # For now, if the endpoint responds, we're started
    return HealthResponse(
        status="started",
        timestamp=datetime.utcnow(),
        version="0.0.0",
        environment=settings.ENVIRONMENT,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )


__all__ = ["router"]

