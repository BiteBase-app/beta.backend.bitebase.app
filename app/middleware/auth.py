import functools
from http import HTTPStatus
from typing import Annotated, Callable, Dict, Any, Optional
import time

try:
    import jwt
    from jwt import PyJWKClient
    JWT_AVAILABLE = True
except ImportError:
    print("JWT module not available, authentication will be disabled")
    JWT_AVAILABLE = False

from fastapi import Depends, HTTPException, WebSocket, WebSocketException, status
from fastapi.requests import HTTPConnection
from pydantic import BaseModel
from starlette.requests import Request

class AuthConfig(BaseModel):
    jwks_url: str
    audience: str
    header: str

class User(BaseModel):
    sub: str
    user_id: str | None = None
    name: str = ""
    email: str = ""
    picture: str | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.sub != "anonymous"

class JWTError(Exception):
    """Exception raised for JWT validation errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

def get_token_from_header(request: HTTPConnection, header_name: str) -> Optional[str]:
    """Extract the JWT token from the request header."""
    auth_header = request.headers.get(header_name)
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]

async def validate_token(token: str, auth_config: AuthConfig) -> Dict[str, Any]:
    """Validate the JWT token using the JWKS endpoint."""
    if not JWT_AVAILABLE:
        raise JWTError("JWT validation is not available")

    try:
        jwks_client = PyJWKClient(auth_config.jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=auth_config.audience,
            options={"verify_exp": True}
        )

        # Check if token is expired
        if "exp" in payload and payload["exp"] < time.time():
            raise JWTError("Token has expired")

        return payload
    except jwt.PyJWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise JWTError(f"Token validation failed: {str(e)}")

async def get_authorized_user(request: Request) -> User:
    """Extract and validate the user from the request.

    This function extracts the JWT token from the request header,
    validates it, and returns a User object with the claims from the token.
    If authentication is disabled or the token is invalid, returns an anonymous user.
    """
    # If auth is not configured, return anonymous user
    if not hasattr(request.app.state, "auth_config") or request.app.state.auth_config is None:
        return User(sub="anonymous")

    auth_config = request.app.state.auth_config
    token = get_token_from_header(request, auth_config.header)

    if not token:
        return User(sub="anonymous")

    try:
        if not JWT_AVAILABLE:
            # For development without JWT validation
            return User(sub="anonymous")

        payload = await validate_token(token, auth_config)

        return User(
            sub=payload.get("sub", "anonymous"),
            user_id=payload.get("user_id"),
            name=payload.get("name", ""),
            email=payload.get("email", ""),
            picture=payload.get("picture")
        )
    except JWTError as e:
        # Log the error but don't raise an exception
        print(f"Authentication error: {str(e)}")
        return User(sub="anonymous")

# Dependency for requiring authentication
def require_auth(user: User = Depends(get_authorized_user)):
    """Dependency that requires an authenticated user.

    Raises an HTTP 401 Unauthorized exception if the user is not authenticated.
    """
    if not user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user