"""
Rate Limiting Middleware
Phase 4: API protection against abuse
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    
    For production, use Redis-backed rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}  # {client_id: [timestamp1, timestamp2, ...]}
        
        # Endpoint-specific limits
        self.endpoint_limits = {
            "/api/auth/login": 5,  # 5 requests per minute
            "/api/auth/register": 3,  # 3 requests per minute
            "/api/config/upload": 20,  # 20 uploads per minute
            "/api/audit": 10,  # 10 audits per minute
        }
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get client identifier
        
        Priority:
        1. Authenticated user ID
        2. IP address
        """
        # Check for authenticated user
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, decode token to get user ID
            # For now, use IP + token prefix
            token_prefix = auth_header[7:20]  # First few chars
            return f"user:{token_prefix}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _get_rate_limit(self, path: str) -> int:
        """Get rate limit for specific endpoint"""
        for endpoint, limit in self.endpoint_limits.items():
            if path.startswith(endpoint):
                return limit
        return self.requests_per_minute
    
    def _is_rate_limited(self, client_id: str, limit: int) -> Tuple[bool, int]:
        """
        Check if client is rate limited
        
        Returns:
            (is_limited, remaining_requests)
        """
        now = time.time()
        minute_ago = now - 60
        
        # Get requests for this client
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests (older than 1 minute)
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Check if over limit
        current_count = len(self.requests[client_id])
        remaining = max(0, limit - current_count)
        
        return current_count >= limit, remaining
    
    def _cleanup_old_entries(self):
        """Periodic cleanup of old request records"""
        now = time.time()
        minute_ago = now - 60
        
        # Remove clients with no recent requests
        clients_to_remove = []
        for client_id, timestamps in self.requests.items():
            # Remove old timestamps
            self.requests[client_id] = [
                ts for ts in timestamps if ts > minute_ago
            ]
            # Mark empty clients for removal
            if not self.requests[client_id]:
                clients_to_remove.append(client_id)
        
        # Remove empty clients
        for client_id in clients_to_remove:
            del self.requests[client_id]
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/detailed", "/"]:
            return await call_next(request)
        
        # Get client identifier
        client_id = self._get_client_id(request)
        
        # Get rate limit for this endpoint
        limit = self._get_rate_limit(request.url.path)
        
        # Check rate limit
        is_limited, remaining = self._is_rate_limited(client_id, limit)
        
        if is_limited:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Maximum {limit} requests per minute.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self.requests[client_id].append(time.time())
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        # Periodic cleanup (every ~100 requests)
        if len(self.requests) > 100:
            self._cleanup_old_entries()
        
        return response
