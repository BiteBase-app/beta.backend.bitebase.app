import logging
import sys
import uuid
from typing import Dict, Any, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Create a logger
logger = logging.getLogger("bitebase")

class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add a unique request ID to each request."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        # Add request_id to request state
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Add request_id to response headers
        response.headers["X-Request-ID"] = request_id
        return response

def get_request_id(request: Request) -> str:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", str(uuid.uuid4()))

def log_info(message: str, request: Optional[Request] = None, extra: Dict[str, Any] = None) -> None:
    """Log an info message with request ID if available."""
    _log(logging.INFO, message, request, extra)

def log_error(message: str, request: Optional[Request] = None, extra: Dict[str, Any] = None) -> None:
    """Log an error message with request ID if available."""
    _log(logging.ERROR, message, request, extra)

def log_warning(message: str, request: Optional[Request] = None, extra: Dict[str, Any] = None) -> None:
    """Log a warning message with request ID if available."""
    _log(logging.WARNING, message, request, extra)

def log_debug(message: str, request: Optional[Request] = None, extra: Dict[str, Any] = None) -> None:
    """Log a debug message with request ID if available."""
    _log(logging.DEBUG, message, request, extra)

def _log(level: int, message: str, request: Optional[Request] = None, extra: Dict[str, Any] = None) -> None:
    """Log a message with the given level and request ID if available."""
    log_extra = extra or {}
    
    if request:
        log_extra["request_id"] = get_request_id(request)
        log_extra["path"] = request.url.path
        log_extra["method"] = request.method
    
    logger.log(level, message, extra=log_extra)
