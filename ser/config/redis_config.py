"""Redis configuration for Tío Pepe system."""

from typing import Dict, Any
from redis import Redis
from functools import wraps
import json
import logging
from config.config import get_config

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for Tío Pepe system."""
    
    def __init__(self):
        """Initialize Redis connection using configuration."""
        config = get_config()
        redis_config = config.get('redis', {})
        
        # Connection pool settings
        pool = Redis.from_url(
            url=redis_config.get('url', 'redis://localhost:6379/0'),
            decode_responses=True,
            socket_timeout=redis_config.get('socket_timeout', 5),
            socket_connect_timeout=redis_config.get('socket_connect_timeout', 3),
            retry_on_timeout=redis_config.get('retry_on_timeout', True),
            max_connections=redis_config.get('max_connections', 50),
            health_check_interval=redis_config.get('health_check_interval', 30),
            retry=3,  # Number of retries for failed operations
            encoding='utf-8',
            encoding_errors='strict',
            socket_keepalive=True
        )
        
        self.redis_client = Redis(connection_pool=pool)
        self.default_ttl = redis_config.get('default_ttl', 3600)  # 1 hour default
        self.cache_prefix = redis_config.get('cache_prefix', 'tiope')
        self.enable_compression = redis_config.get('enable_compression', True)
        self.compression_threshold = redis_config.get('compression_threshold', 1024)  # 1KB
    
    def cache_key(self, prefix: str, identifier: str) -> str:
        """Generate a cache key with prefix."""
        return f"{self.cache_prefix}:{prefix}:{identifier}"
    
    def get(self, key: str) -> Any:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with optional TTL."""
        try:
            ttl = ttl or self.default_ttl
            return self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

def cache_response(prefix: str, ttl: int = None):
    """Decorator for caching API responses."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key from function arguments
            key_parts = [str(arg) for arg in args]
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = cache.cache_key(prefix, ":".join(key_parts))
            
            # Try to get from cache first
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # If not in cache, execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator