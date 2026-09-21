"""
Security Headers Middleware
Phase 8: Security hardening
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    
    Implements OWASP security header recommendations
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable browser XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent MIME type sniffing
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        csp = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ])
        response.headers["Content-Security-Policy"] = csp
        
        # Strict Transport Security (HSTS)
        # Only enable in production with HTTPS
        if not request.url.hostname in ["localhost", "127.0.0.1"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature-Policy)
        permissions = "; ".join([
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()"
        ])
        response.headers["Permissions-Policy"] = permissions
        
        # Remove server header
        response.headers.pop("Server", None)
        
        # Add custom security headers
        response.headers["X-Content-Security-Policy"] = csp
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        
        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Secure CORS handling
    
    Only allows specific origins in production
    """
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("Origin")
        
        response = await call_next(request)
        
        # Check if origin is allowed
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Request-ID"
            response.headers["Access-Control-Max-Age"] = "3600"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request
    
    Useful for tracing and debugging
    """
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add to response
        response.headers["X-Request-ID"] = request_id
        
        return response
