from typing import Dict, Any, Optional, List, Type
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.apis.models.base import BaseResponse
from app.core.logging import log_error

class AppError(Exception):
    """Base class for application errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"
    message: str = "An internal error occurred"
    
    def __init__(self, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)

class NotFoundError(AppError):
    """Error raised when a resource is not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"
    message = "Resource not found"

class ValidationError(AppError):
    """Error raised when validation fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "validation_error"
    message = "Validation error"

class AuthenticationError(AppError):
    """Error raised when authentication fails."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_error"
    message = "Authentication failed"

class AuthorizationError(AppError):
    """Error raised when authorization fails."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "authorization_error"
    message = "Not authorized to access this resource"

class RateLimitError(AppError):
    """Error raised when rate limit is exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "rate_limit_exceeded"
    message = "Rate limit exceeded"

class ExternalServiceError(AppError):
    """Error raised when an external service fails."""
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "external_service_error"
    message = "External service error"

# Error handlers
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions."""
    log_error(f"AppError: {exc.message}", request, {"error_code": exc.error_code, "details": exc.details})
    
    response_data = {
        "success": False,
        "message": exc.message,
        "error": {
            "code": exc.error_code,
            "details": exc.details
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )

async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle RequestValidationError exceptions."""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_detail)
    
    log_error("Validation error", request, {"errors": errors})
    
    response_data = {
        "success": False,
        "message": "Validation error",
        "error": {
            "code": "validation_error",
            "details": {"errors": errors}
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )

async def pydantic_validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic ValidationError exceptions."""
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", "")
        }
        errors.append(error_detail)
    
    log_error("Pydantic validation error", request, {"errors": errors})
    
    response_data = {
        "success": False,
        "message": "Validation error",
        "error": {
            "code": "validation_error",
            "details": {"errors": errors}
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )

async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic exceptions."""
    log_error(f"Unhandled exception: {str(exc)}", request)
    
    response_data = {
        "success": False,
        "message": "An internal server error occurred",
        "error": {
            "code": "internal_error",
            "details": None
        }
    }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )

def register_exception_handlers(app):
    """Register all exception handlers with the FastAPI app."""
    from fastapi.exceptions import RequestValidationError
    from pydantic import ValidationError
    
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_error_handler)
    app.add_exception_handler(Exception, http_exception_handler)
