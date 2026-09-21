"""
Logging Middleware
Phase 4: Structured logging for all requests
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging

# Configure structured logger
logger = logging.getLogger("vajra.api")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all API requests with structured data
    """
    
    async def dispatch(self, request: Request, call_next):
        # Start time
        start_time = time.time()
        
        # Get request ID
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Extract user info if available
        user_info = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            user_info = "authenticated"  # In production, decode token
        
        # Log request
        logger.info(
            "request_started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "authenticated": user_info is not None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                "request_completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "authenticated": user_info is not None,
                }
            )
            
            # Add timing header
            response.headers["X-Response-Time"] = f"{round(duration_ms, 2)}ms"
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                "request_failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error": str(e),
                    "error_type": type(e).__name__,
                }
            )
            raise
