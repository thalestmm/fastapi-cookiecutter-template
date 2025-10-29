"""
Schema models for health check endpoints.
"""
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Current server time")
    version: str = Field(default="0.0.0", description="Application version")
    environment: str = Field(..., description="Current environment")
    python_version: str = Field(..., description="Python version")
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "version": "1.0.0",
                "environment": "development",
                "python_version": "3.14.0"
            }]
        }
    }


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    python_version: str
    services: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "healthy",
                "timestamp": "2024-01-01T12:00:00",
                "version": "1.0.0",
                "environment": "development",
                "python_version": "3.14.0",
                "services": {
                    "redis": {"status": "healthy"},
                    "celery": {"status": "healthy", "workers": 1}
                }
            }]
        }
    }


__all__ = ["HealthResponse", "DetailedHealthResponse"]

