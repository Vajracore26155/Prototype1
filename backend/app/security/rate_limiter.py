"""
Advanced Rate Limiting
Phase 8: Security hardening with sliding window rate limits
"""
from fastapi import HTTPException, Request
from typing import Optional, Dict
from datetime import datetime, timedelta
from collections import deque
import time


class RateLimiter:
    """
    Sliding window rate limiter
    
    Tracks requests per time window with token bucket algorithm
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_size = burst_size
        
        # Storage: {client_id: deque of timestamps}
        self.minute_windows: Dict[str, deque] = {}
        self.hour_windows: Dict[str, deque] = {}
        
        # Token buckets: {client_id: (tokens, last_refill)}
        self.buckets: Dict[str, tuple] = {}
    
    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier
        
        Uses IP + User-Agent for anonymous, user_id for authenticated
        """
        # Try to get authenticated user
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP + User-Agent
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        return f"ip:{client_ip}:{hash(user_agent)}"
    
    def _clean_old_requests(self, window: deque, max_age: int):
        """Remove requests older than max_age seconds"""
        now = time.time()
        while window and window[0] < now - max_age:
            window.popleft()
    
    def check_rate_limit(self, request: Request) -> bool:
        """
        Check if request is within rate limits
        
        Returns True if allowed, raises HTTPException if blocked
        """
        client_id = self._get_client_id(request)
        now = time.time()
        
        # Initialize windows if needed
        if client_id not in self.minute_windows:
            self.minute_windows[client_id] = deque()
        if client_id not in self.hour_windows:
            self.hour_windows[client_id] = deque()
        
        # Clean old requests
        self._clean_old_requests(self.minute_windows[client_id], 60)
        self._clean_old_requests(self.hour_windows[client_id], 3600)
        
        # Check minute limit
        if len(self.minute_windows[client_id]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_minute,
                    "window": "minute",
                    "retry_after": 60
                }
            )
        
        # Check hour limit
        if len(self.hour_windows[client_id]) >= self.requests_per_hour:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests_per_hour,
                    "window": "hour",
                    "retry_after": 3600
                }
            )
        
        # Check burst limit (token bucket)
        if not self._check_burst_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Burst limit exceeded",
                    "limit": self.burst_size,
                    "retry_after": 1
                }
            )
        
        # Record request
        self.minute_windows[client_id].append(now)
        self.hour_windows[client_id].append(now)
        
        return True
    
    def _check_burst_limit(self, client_id: str) -> bool:
        """
        Check token bucket for burst protection
        
        Refills at 1 token per second, max burst_size tokens
        """
        now = time.time()
        
        if client_id not in self.buckets:
            self.buckets[client_id] = (self.burst_size - 1, now)
            return True
        
        tokens, last_refill = self.buckets[client_id]
        
        # Refill tokens (1 per second)
        elapsed = now - last_refill
        tokens = min(self.burst_size, tokens + elapsed)
        
        if tokens < 1:
            return False
        
        # Consume token
        self.buckets[client_id] = (tokens - 1, now)
        return True
    
    def get_remaining(self, request: Request) -> Dict:
        """Get remaining requests for client"""
        client_id = self._get_client_id(request)
        
        # Clean windows
        if client_id in self.minute_windows:
            self._clean_old_requests(self.minute_windows[client_id], 60)
        if client_id in self.hour_windows:
            self._clean_old_requests(self.hour_windows[client_id], 3600)
        
        minute_used = len(self.minute_windows.get(client_id, []))
        hour_used = len(self.hour_windows.get(client_id, []))
        
        return {
            "minute": {
                "limit": self.requests_per_minute,
                "used": minute_used,
                "remaining": self.requests_per_minute - minute_used
            },
            "hour": {
                "limit": self.requests_per_hour,
                "used": hour_used,
                "remaining": self.requests_per_hour - hour_used
            }
        }


# Global rate limiter instances
default_rate_limiter = RateLimiter(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_size=10
)

auth_rate_limiter = RateLimiter(
    requests_per_minute=5,
    requests_per_hour=100,
    burst_size=3
)

upload_rate_limiter = RateLimiter(
    requests_per_minute=10,
    requests_per_hour=100,
    burst_size=2
)
