from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Type
from fastapi import APIRouter, FastAPI, Depends, Request, Response
import re

class APIVersion(str, Enum):
    """API version enum."""
    V1 = "v1"
    V2 = "v2"
    
    @classmethod
    def latest(cls) -> "APIVersion":
        """Get the latest API version."""
        return cls.V1  # Update this when new versions are added
    
    @classmethod
    def all(cls) -> List["APIVersion"]:
        """Get all API versions."""
        return [v for v in cls]
    
    @classmethod
    def from_string(cls, version: str) -> "APIVersion":
        """Convert string to APIVersion."""
        try:
            return cls(version.lower())
        except ValueError:
            return cls.latest()

class VersionedAPIRouter(APIRouter):
    """Router with API versioning support."""
    
    def __init__(
        self,
        version: APIVersion,
        prefix: str = "",
        tags: List[str] = None,
        **kwargs
    ):
        """Initialize versioned router."""
        self.api_version = version
        
        # Add version to prefix
        versioned_prefix = f"/api/{version.value}{prefix}"
        
        # Add version to tags if not present
        if tags is None:
            tags = []
        if version.value not in tags:
            tags.append(version.value)
        
        super().__init__(prefix=versioned_prefix, tags=tags, **kwargs)

def create_versioned_routers(app: FastAPI, versions: List[APIVersion] = None):
    """Create versioned API routers for the application."""
    if versions is None:
        versions = APIVersion.all()
    
    routers = {}
    for version in versions:
        router = APIRouter(prefix=f"/api/{version.value}", tags=[version.value])
        app.include_router(router)
        routers[version] = router
    
    return routers

def version_response(response_data: Dict[str, Any], version: APIVersion) -> Dict[str, Any]:
    """Version a response based on API version."""
    # Add version to response
    response_data["api_version"] = version.value
    
    # Handle version-specific transformations
    if version == APIVersion.V1:
        # V1 format is the default
        return response_data
    elif version == APIVersion.V2:
        # Example V2 transformation: flatten nested data
        if "data" in response_data and isinstance(response_data["data"], dict):
            for key, value in response_data["data"].items():
                if key not in response_data:
                    response_data[key] = value
            # Keep data for backward compatibility
        return response_data
    
    # Default case
    return response_data

def get_version_from_request(request: Request) -> APIVersion:
    """Extract API version from request path."""
    path = request.url.path
    match = re.search(r"/api/(v\d+)/", path)
    if match:
        version_str = match.group(1)
        return APIVersion.from_string(version_str)
    return APIVersion.latest()

class VersionedResponse(Response):
    """Response class that handles API versioning."""
    
    def render(self, content: Any) -> bytes:
        """Render response with version-specific transformations."""
        if isinstance(content, dict):
            # Get version from request
            version = get_version_from_request(self.request)
            
            # Apply version-specific transformations
            content = version_response(content, version)
        
        return super().render(content)
