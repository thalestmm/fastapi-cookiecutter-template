"""
Custom middleware for the FastAPI application.

This module contains middleware for request logging, error handling,
and other cross-cutting concerns.
"""
import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and outgoing responses.
    
    Logs:
    - Request method, path, query params
    - Request ID for tracing
    - Processing time
    - Response status code
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain
        
        Returns:
            Response: HTTP response
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started | "
            f"ID: {request_id} | "
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log response
            logger.info(
                f"Request completed | "
                f"ID: {request_id} | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.4f}s"
            )
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | "
                f"ID: {request_id} | "
                f"Error: {str(e)} | "
                f"Duration: {process_time:.4f}s",
                exc_info=True
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle uncaught exceptions and return proper JSON responses.
    
    Catches any unhandled exceptions and returns a standardized error response.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and handle any exceptions.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain
        
        Returns:
            Response: HTTP response or error response
        """
        try:
            response = await call_next(request)
            return response
            
        except ValueError as e:
            logger.warning(f"ValueError in request: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "Bad Request",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except PermissionError as e:
            logger.warning(f"PermissionError in request: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Forbidden",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except FileNotFoundError as e:
            logger.warning(f"FileNotFoundError in request: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "error": "Not Found",
                    "message": str(e),
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
            
        except Exception as e:
            # Log the full exception
            logger.error(
                f"Unhandled exception in request: {str(e)}",
                exc_info=True
            )
            
            # Return different response based on environment
            if settings.ENVIRONMENT == "production":
                error_message = "An internal error occurred"
            else:
                error_message = str(e)
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": error_message,
                    "request_id": getattr(request.state, "request_id", None)
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Adds headers like:
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Strict-Transport-Security (in production)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and add security headers.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain
        
        Returns:
            Response: HTTP response with security headers
        """
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Add HSTS header in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitInfo:
    """Simple rate limit tracking (in-memory, for demonstration)."""
    
    def __init__(self):
        self.requests = {}
        self.window = 60  # 1 minute window
        self.max_requests = 100  # Max requests per window
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed based on rate limit."""
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if current_time - req_time < self.window
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(current_time)
            return True
        
        return False


# Global rate limit tracker (for demonstration; use Redis in production)
rate_limiter = RateLimitInfo()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    
    Note: This uses in-memory storage and is suitable for single-instance deployments.
    For production with multiple instances, use Redis-based rate limiting.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and enforce rate limits.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/endpoint in chain
        
        Returns:
            Response: HTTP response or 429 Too Many Requests
        """
        # Skip rate limiting for health checks and docs
        if request.url.path.startswith("/health") or request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Too Many Requests",
                    "message": "Rate limit exceeded. Please try again later.",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )
        
        return await call_next(request)


__all__ = [
    "RequestLoggingMiddleware",
    "ErrorHandlingMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimitMiddleware",
]

