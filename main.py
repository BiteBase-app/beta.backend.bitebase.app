import os
import time
import asyncio
from fastapi import FastAPI, APIRouter, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import TypeVar, Callable, List, Dict, Any
from app.config import config
from app.middleware.auth import AuthConfig, get_authorized_user, require_auth
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.core.logging import RequestIdMiddleware, log_info, log_error, log_warning
from app.core.errors import register_exception_handlers

# Import optional modules with fallbacks
try:
    from app.core.monitoring import MetricsMiddleware, setup_prometheus_endpoint, metrics
    MONITORING_AVAILABLE = True
except ImportError:
    log_warning("Monitoring module not available")
    MONITORING_AVAILABLE = False
    # Create dummy classes/functions
    class MetricsMiddleware:
        def __init__(self, app):
            self.app = app
        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)
    def setup_prometheus_endpoint(app):
        pass
    metrics = None

try:
    from app.core.versioning import APIVersion, VersionedAPIRouter, create_versioned_routers
    VERSIONING_AVAILABLE = True
except ImportError:
    log_warning("API versioning module not available")
    VERSIONING_AVAILABLE = False
    # Create dummy classes/functions
    class APIVersion:
        V1 = "v1"
        @classmethod
        def all(cls):
            return [cls.V1]
    class VersionedAPIRouter(APIRouter):
        pass
    def create_versioned_routers(app, versions=None):
        return {}

try:
    from app.core.database import database_client
    DATABASE_AVAILABLE = True
except ImportError:
    log_warning("Database module not available")
    DATABASE_AVAILABLE = False
    database_client = None

try:
    from app.core.cache import cache
    CACHE_AVAILABLE = True
except ImportError:
    log_warning("Cache module not available")
    CACHE_AVAILABLE = False
    cache = None

# Define a custom type for BiteBase Intelligence APIs
BiteBaseIntelligenceAPIs = TypeVar('BiteBaseIntelligenceAPIs', bound=FastAPI)

# API version
API_VERSION = "1.0.0"

def import_api_routers() -> APIRouter:
    """Import and combine all API routers"""
    router = APIRouter()

    # Import your API routers here
    from app.apis.user import router as user_router
    from app.apis.auth import router as auth_router
    from app.apis.langflow import router as langflow_router
    from app.apis.foot_traffic import router as foot_traffic_router

    # Include all routers
    router.include_router(user_router)
    router.include_router(auth_router)
    router.include_router(langflow_router)
    router.include_router(foot_traffic_router)

    return router

# Middleware to log request timing
class TimingMiddleware:
    """Middleware to log request timing."""

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        log_info(f"Request processed in {process_time:.4f} seconds", request)
        return response

def create_app() -> BiteBaseIntelligenceAPIs:
    """Create the app. This is called by uvicorn with the factory option to construct the app object."""
    app = FastAPI(
        title="BiteBase Intelligence API",
        description="API for BiteBase Intelligence platform",
        version=API_VERSION,
        docs_url="/docs" if not config.is_production else None,  # Disable docs in production
        redoc_url="/redoc" if not config.is_production else None,  # Disable redoc in production
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Initialize database if available
    if DATABASE_AVAILABLE and database_client is not None:
        try:
            database_client.initialize()
            if not config.is_production:
                database_client.create_tables()
        except Exception as e:
            log_error(f"Failed to initialize database: {str(e)}")
    else:
        log_warning("Database integration is not available")

    # Initialize cache if available
    if CACHE_AVAILABLE and cache is not None:
        try:
            cache.initialize()
        except Exception as e:
            log_error(f"Failed to initialize cache: {str(e)}")
    else:
        log_warning("Cache integration is not available")

    # Add middlewares
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # Add metrics middleware if available
    if MONITORING_AVAILABLE:
        app.add_middleware(MetricsMiddleware)

    # Add rate limiting in production
    if config.is_production:
        app.add_middleware(
            RateLimitMiddleware,
            rate_limit=100,  # 100 requests per minute
            exclude_paths=["/docs", "/redoc", "/openapi.json", "/test", "/metrics", "/health"]
        )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if not config.is_production else ["https://bitebase.app", "https://*.bitebase.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add timing middleware
    app.middleware("http")(TimingMiddleware())

    # Set up versioned API routers if available
    if VERSIONING_AVAILABLE:
        create_versioned_routers(app, [APIVersion.V1])

    # Include API routers
    app.include_router(import_api_routers())

    # Set up Prometheus metrics endpoint if available
    if MONITORING_AVAILABLE:
        setup_prometheus_endpoint(app)

    # Log all routes
    for route in app.routes:
        if hasattr(route, "methods"):
            for method in route.methods:
                log_info(f"Route registered: {method} {route.path}")

    # Configure Firebase authentication
    firebase_cfg = config.firebase_config
    if all(firebase_cfg.values()):
        log_info("Firebase config found")
        auth_config = {
            "jwks_url": "https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com",
            "audience": firebase_cfg["project_id"],
            "header": "authorization",
        }
        app.state.auth_config = AuthConfig(**auth_config)
    else:
        log_info("Warning: Firebase configuration is incomplete. Running without authentication.")
        app.state.auth_config = None

    return app

app = create_app()

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify backend configuration"""
    return {
        "status": "ok",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "firebase_configured": bool(config.firebase_config["project_id"]),
        "routes_loaded": len(app.routes),
        "api_version": API_VERSION
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring systems"""
    # Check database connection
    if DATABASE_AVAILABLE and database_client is not None:
        db_status = "connected"
        try:
            if hasattr(database_client, "engine") and database_client.engine:
                with database_client.get_session() as session:
                    session.execute("SELECT 1")
            else:
                db_status = "not_configured"
        except Exception as e:
            db_status = f"error: {str(e)}"
    else:
        db_status = "not_available"

    # Check cache connection
    if CACHE_AVAILABLE and cache is not None:
        cache_status = "connected"
        try:
            if hasattr(cache, "redis_client") and cache.redis_client:
                cache.redis_client.ping()
            else:
                cache_status = "in_memory"
        except Exception as e:
            cache_status = f"error: {str(e)}"
    else:
        cache_status = "not_available"

    # Get system info
    import platform

    # Try to import psutil for system metrics
    try:
        import psutil
        system_info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent
        }
    except ImportError:
        system_info = {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_usage": "psutil not available",
            "memory_usage": "psutil not available"
        }

    # Get available modules
    modules_status = {
        "database": DATABASE_AVAILABLE,
        "cache": CACHE_AVAILABLE,
        "monitoring": MONITORING_AVAILABLE,
        "versioning": VERSIONING_AVAILABLE
    }

    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": API_VERSION,
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "modules": modules_status,
        "database": {
            "status": db_status
        },
        "cache": {
            "status": cache_status,
            "type": "redis" if CACHE_AVAILABLE and hasattr(cache, "redis_client") and cache.redis_client else "in_memory"
        },
        "system": system_info
    }

@app.get("/protected-test")
async def protected_test(user = Depends(require_auth)):
    """Test endpoint that requires authentication"""
    return {
        "status": "ok",
        "user": user.dict(),
        "message": "You are authenticated!"
    }
