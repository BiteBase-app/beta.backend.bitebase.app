import os
import time
import json
import socket
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import log_info, log_error, log_warning

# Try to import psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    log_warning("psutil not available, system metrics will be limited")
    PSUTIL_AVAILABLE = False

# Try to import prometheus_client
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    log_warning("Prometheus client not available, metrics collection will be limited")
    PROMETHEUS_AVAILABLE = False

class Metrics:
    """Metrics collection for monitoring."""

    def __init__(self):
        self.initialized = False
        self.metrics = {}

        try:
            self.initialize()
        except Exception as e:
            log_error(f"Failed to initialize metrics: {str(e)}")

    def initialize(self):
        """Initialize metrics collection."""
        if self.initialized:
            return

        if PROMETHEUS_AVAILABLE:
            # HTTP request metrics
            self.metrics["http_requests_total"] = Counter(
                "http_requests_total",
                "Total number of HTTP requests",
                ["method", "endpoint", "status"]
            )

            self.metrics["http_request_duration_seconds"] = Histogram(
                "http_request_duration_seconds",
                "HTTP request duration in seconds",
                ["method", "endpoint"],
                buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, 25.0, 50.0, 75.0, 100.0, float("inf"))
            )

            self.metrics["http_requests_in_progress"] = Gauge(
                "http_requests_in_progress",
                "Number of HTTP requests in progress",
                ["method"]
            )

            # System metrics
            self.metrics["system_cpu_usage"] = Gauge(
                "system_cpu_usage",
                "System CPU usage"
            )

            self.metrics["system_memory_usage"] = Gauge(
                "system_memory_usage",
                "System memory usage in bytes"
            )

            self.metrics["system_info"] = Info(
                "system_info",
                "System information"
            )

            # Application metrics
            self.metrics["app_info"] = Info(
                "app_info",
                "Application information"
            )

            # Set system info
            self.metrics["system_info"].info({
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": str(psutil.cpu_count())
            })

            # Set app info
            self.metrics["app_info"].info({
                "version": os.getenv("APP_VERSION", "1.0.0"),
                "environment": os.getenv("ENVIRONMENT", "development")
            })

            log_info("Prometheus metrics initialized")
        else:
            # Simple in-memory metrics
            self.metrics = {
                "requests": {
                    "total": 0,
                    "by_endpoint": {},
                    "by_status": {},
                    "by_method": {}
                },
                "errors": {
                    "total": 0,
                    "by_type": {}
                },
                "performance": {
                    "request_durations": []
                }
            }
            log_info("In-memory metrics initialized")

        self.initialized = True

    def track_request(self, request: Request, response: Response, duration: float):
        """Track HTTP request metrics."""
        if not self.initialized:
            self.initialize()

        try:
            method = request.method
            endpoint = request.url.path
            status = response.status_code

            if PROMETHEUS_AVAILABLE:
                self.metrics["http_requests_total"].labels(
                    method=method,
                    endpoint=endpoint,
                    status=status
                ).inc()

                self.metrics["http_request_duration_seconds"].labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
            else:
                # Update in-memory metrics
                self.metrics["requests"]["total"] += 1

                # By endpoint
                if endpoint not in self.metrics["requests"]["by_endpoint"]:
                    self.metrics["requests"]["by_endpoint"][endpoint] = 0
                self.metrics["requests"]["by_endpoint"][endpoint] += 1

                # By status
                status_str = str(status)
                if status_str not in self.metrics["requests"]["by_status"]:
                    self.metrics["requests"]["by_status"][status_str] = 0
                self.metrics["requests"]["by_status"][status_str] += 1

                # By method
                if method not in self.metrics["requests"]["by_method"]:
                    self.metrics["requests"]["by_method"][method] = 0
                self.metrics["requests"]["by_method"][method] += 1

                # Track duration
                self.metrics["performance"]["request_durations"].append({
                    "endpoint": endpoint,
                    "method": method,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                })

                # Keep only last 1000 durations
                if len(self.metrics["performance"]["request_durations"]) > 1000:
                    self.metrics["performance"]["request_durations"] = self.metrics["performance"]["request_durations"][-1000:]
        except Exception as e:
            log_error(f"Error tracking request metrics: {str(e)}")

    def track_error(self, error_type: str, error_message: str):
        """Track error metrics."""
        if not self.initialized:
            self.initialize()

        try:
            if not PROMETHEUS_AVAILABLE:
                # Update in-memory metrics
                self.metrics["errors"]["total"] += 1

                # By type
                if error_type not in self.metrics["errors"]["by_type"]:
                    self.metrics["errors"]["by_type"][error_type] = 0
                self.metrics["errors"]["by_type"][error_type] += 1
        except Exception as e:
            log_error(f"Error tracking error metrics: {str(e)}")

    def update_system_metrics(self):
        """Update system metrics."""
        if not self.initialized:
            return

        try:
            if PROMETHEUS_AVAILABLE and PSUTIL_AVAILABLE:
                # Update CPU usage
                self.metrics["system_cpu_usage"].set(psutil.cpu_percent())

                # Update memory usage
                memory = psutil.virtual_memory()
                self.metrics["system_memory_usage"].set(memory.used)
            elif not PROMETHEUS_AVAILABLE:
                # Skip if Prometheus is not available
                pass
            elif not PSUTIL_AVAILABLE:
                # Set default values if psutil is not available
                if "system_cpu_usage" in self.metrics:
                    self.metrics["system_cpu_usage"].set(0)
                if "system_memory_usage" in self.metrics:
                    self.metrics["system_memory_usage"].set(0)
        except Exception as e:
            log_error(f"Error updating system metrics: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        if not self.initialized:
            self.initialize()

        if PROMETHEUS_AVAILABLE:
            return {"message": "Prometheus metrics available at /metrics endpoint"}
        else:
            return self.metrics

# Create a singleton instance
metrics = Metrics()

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics."""

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)

        # Track request in progress
        if PROMETHEUS_AVAILABLE:
            metrics.metrics["http_requests_in_progress"].labels(
                method=request.method
            ).inc()

        # Process request and track duration
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            metrics.track_request(request, response, duration)
            return response
        except Exception as e:
            duration = time.time() - start_time
            # Create a 500 response for metrics
            response = Response(
                content=json.dumps({"detail": str(e)}),
                status_code=500,
                media_type="application/json"
            )
            metrics.track_request(request, response, duration)
            metrics.track_error("unhandled_exception", str(e))
            raise
        finally:
            # Decrement in-progress counter
            if PROMETHEUS_AVAILABLE:
                metrics.metrics["http_requests_in_progress"].labels(
                    method=request.method
                ).dec()

def setup_prometheus_endpoint(app):
    """Set up Prometheus metrics endpoint."""
    if not PROMETHEUS_AVAILABLE:
        return

    @app.get("/metrics")
    async def metrics_endpoint():
        """Expose Prometheus metrics."""
        # Update system metrics before returning
        metrics.update_system_metrics()
        return Response(
            content=prometheus_client.generate_latest(),
            media_type="text/plain"
        )
