from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List, Dict, Optional, Callable
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to implement rate limiting."""
    
    def __init__(
        self, 
        app,
        rate_limit: int = 100,  # Requests per minute
        window_size: int = 60,  # Window size in seconds
        exclude_paths: Optional[List[str]] = None
    ):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window_size = window_size
        self.exclude_paths = exclude_paths or []
        self.requests = {}  # IP -> List of timestamps
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_time = time.time()
        if client_ip in self.requests:
            # Remove old timestamps
            self.requests[client_ip] = [
                ts for ts in self.requests[client_ip] 
                if current_time - ts < self.window_size
            ]
            
            # Check if rate limit is exceeded
            if len(self.requests[client_ip]) >= self.rate_limit:
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": str(self.window_size)}
                )
        else:
            self.requests[client_ip] = []
        
        # Add current timestamp
        self.requests[client_ip].append(current_time)
        
        # Process the request
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
