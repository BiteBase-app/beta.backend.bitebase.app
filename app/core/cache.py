import os
import json
import time
import hashlib
from typing import Dict, Any, Optional, Callable, TypeVar, Generic, Union
from functools import wraps
from datetime import datetime, timedelta

from app.core.logging import log_info, log_error, log_warning

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    log_warning("Redis not available, using in-memory cache instead")
    REDIS_AVAILABLE = False

T = TypeVar('T')

class Cache:
    """Cache implementation with Redis or in-memory fallback."""
    
    def __init__(self):
        self.redis_client = None
        self.in_memory_cache = {}
        self.initialized = False
        
        try:
            self.initialize()
        except Exception as e:
            log_error(f"Failed to initialize cache: {str(e)}")
    
    def initialize(self):
        """Initialize cache with Redis if available, otherwise use in-memory cache."""
        if self.initialized:
            return
            
        # Try to connect to Redis if available
        if REDIS_AVAILABLE:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                try:
                    self.redis_client = redis.from_url(
                        redis_url,
                        socket_timeout=5,
                        socket_connect_timeout=5,
                        socket_keepalive=True,
                        health_check_interval=30
                    )
                    # Test connection
                    self.redis_client.ping()
                    log_info("Redis cache initialized")
                    self.initialized = True
                    return
                except Exception as e:
                    log_error(f"Failed to connect to Redis: {str(e)}")
                    self.redis_client = None
        
        # Fallback to in-memory cache
        log_info("Using in-memory cache")
        self.initialized = True
    
    def _generate_key(self, key: str) -> str:
        """Generate a cache key with namespace."""
        namespace = os.getenv("CACHE_NAMESPACE", "bitebase")
        return f"{namespace}:{key}"
    
    def _serialize(self, value: Any) -> str:
        """Serialize value to string."""
        if isinstance(value, (str, int, float, bool, type(None))):
            return json.dumps(value)
        return json.dumps(value, default=lambda o: o.__dict__ if hasattr(o, "__dict__") else str(o))
    
    def _deserialize(self, value: str) -> Any:
        """Deserialize string to value."""
        if not value:
            return None
        return json.loads(value)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.initialized:
            self.initialize()
            
        cache_key = self._generate_key(key)
        
        try:
            # Try Redis first
            if self.redis_client:
                value = self.redis_client.get(cache_key)
                if value:
                    return self._deserialize(value)
            # Fallback to in-memory cache
            elif cache_key in self.in_memory_cache:
                entry = self.in_memory_cache[cache_key]
                # Check if entry is expired
                if entry["expires_at"] and entry["expires_at"] < time.time():
                    del self.in_memory_cache[cache_key]
                    return None
                return entry["value"]
        except Exception as e:
            log_error(f"Cache get error for key {key}: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL in seconds."""
        if not self.initialized:
            self.initialize()
            
        cache_key = self._generate_key(key)
        
        try:
            # Try Redis first
            if self.redis_client:
                serialized = self._serialize(value)
                if ttl:
                    return bool(self.redis_client.setex(cache_key, ttl, serialized))
                else:
                    return bool(self.redis_client.set(cache_key, serialized))
            # Fallback to in-memory cache
            else:
                expires_at = time.time() + ttl if ttl else None
                self.in_memory_cache[cache_key] = {
                    "value": value,
                    "expires_at": expires_at
                }
                return True
        except Exception as e:
            log_error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.initialized:
            self.initialize()
            
        cache_key = self._generate_key(key)
        
        try:
            # Try Redis first
            if self.redis_client:
                return bool(self.redis_client.delete(cache_key))
            # Fallback to in-memory cache
            elif cache_key in self.in_memory_cache:
                del self.in_memory_cache[cache_key]
                return True
        except Exception as e:
            log_error(f"Cache delete error for key {key}: {str(e)}")
        
        return False
    
    def clear(self, namespace: Optional[str] = None) -> bool:
        """Clear all cache or specific namespace."""
        if not self.initialized:
            self.initialize()
            
        try:
            # Try Redis first
            if self.redis_client:
                if namespace:
                    pattern = f"{namespace}:*"
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        return bool(self.redis_client.delete(*keys))
                else:
                    return bool(self.redis_client.flushdb())
            # Fallback to in-memory cache
            else:
                if namespace:
                    prefix = f"{namespace}:"
                    keys_to_delete = [k for k in self.in_memory_cache.keys() if k.startswith(prefix)]
                    for k in keys_to_delete:
                        del self.in_memory_cache[k]
                else:
                    self.in_memory_cache.clear()
                return True
        except Exception as e:
            log_error(f"Cache clear error: {str(e)}")
            return False

# Create a singleton instance
cache = Cache()

def cached(ttl: int = 300, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                if hasattr(arg, "__dict__"):
                    # Skip request objects
                    if hasattr(arg, "method") and hasattr(arg, "url"):
                        continue
                    key_parts.append(str(hash(frozenset(arg.__dict__.items()))))
                else:
                    key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if hasattr(v, "__dict__"):
                    key_parts.append(f"{k}:{hash(frozenset(v.__dict__.items()))}")
                else:
                    key_parts.append(f"{k}:{v}")
            
            # Create final key
            key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                log_info(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            cache.set(key, result, ttl)
            log_info(f"Cache miss for {func.__name__}, cached for {ttl} seconds")
            return result
        
        return wrapper
    return decorator
