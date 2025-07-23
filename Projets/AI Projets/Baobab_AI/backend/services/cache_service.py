"""Redis cache service for Baobab AI."""

import json
import logging
from typing import Any, Optional, Dict
from datetime import timedelta
import redis
import os

logger = logging.getLogger(__name__)

class CacheService:
    """Redis cache service for application data."""
    
    def __init__(self):
        """Initialize Redis connection."""
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info("Redis cache service initialized successfully")
        except redis.RedisError as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.connected = False
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration."""
        if not self.connected:
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.set(key, serialized_value, ex=expire)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not self.connected:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def set_hash(self, key: str, mapping: Dict[str, Any], expire: Optional[int] = None) -> bool:
        """Set hash in cache."""
        if not self.connected:
            return False
        
        try:
            # Convert values to JSON strings
            serialized_mapping = {
                field: json.dumps(value, default=str) 
                for field, value in mapping.items()
            }
            result = self.redis_client.hset(key, mapping=serialized_mapping)
            if expire:
                self.redis_client.expire(key, expire)
            return bool(result)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.error(f"Cache set hash error for key {key}: {e}")
            return False
    
    def get_hash(self, key: str, field: Optional[str] = None) -> Optional[Any]:
        """Get hash or hash field from cache."""
        if not self.connected:
            return None
        
        try:
            if field:
                value = self.redis_client.hget(key, field)
                if value:
                    return json.loads(value)
                return None
            else:
                hash_data = self.redis_client.hgetall(key)
                if hash_data:
                    return {
                        field: json.loads(value) 
                        for field, value in hash_data.items()
                    }
                return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Cache get hash error for key {key}: {e}")
            return None
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache."""
        if not self.connected:
            return None
        
        try:
            return self.redis_client.incrby(key, amount)
        except redis.RedisError as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.connected:
            return {"connected": False, "error": "Redis not connected"}
        
        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "uptime_in_seconds": info.get("uptime_in_seconds")
            }
        except redis.RedisError as e:
            logger.error(f"Cache stats error: {e}")
            return {"connected": False, "error": str(e)}

# Global cache instance
cache = CacheService()

# Cache decorators
def cache_result(key_prefix: str, expire: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire)
            logger.debug(f"Cache set for {cache_key}")
            return result
        
        return wrapper
    return decorator

def cache_user_data(user_id: int, expire: int = 1800):
    """Cache decorator for user-specific data."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"user:{user_id}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache.set(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator

def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user."""
    pattern = f"user:{user_id}:*"
    return cache.clear_pattern(pattern)

def cache_chat_response(session_id: int, expire: int = 7200):
    """Cache decorator for chat responses."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"chat:{session_id}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            if result:  # Only cache successful responses
                cache.set(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator