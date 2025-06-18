"""
Caching system for OpenFood backend to improve performance
"""
import time
import json
import hashlib
import functools
from typing import Any, Dict, Optional, Callable, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """In-memory cache manager with TTL support"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        # Create a string representation of arguments
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() > entry['expires_at']:
                del self.cache[key]
                self.stats['evictions'] += 1
                self.stats['misses'] += 1
                return None
            
            self.stats['hits'] += 1
            logger.debug(f"Cache HIT: {key}")
            return entry['value']
        
        self.stats['misses'] += 1
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        
        self.stats['sets'] += 1
        logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache DELETE: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        logger.info("Cache cleared")
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats['evictions'] += 1
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2),
            'cache_size': len(self.cache),
            'memory_usage_mb': self._estimate_memory_usage()
        }
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB (rough calculation)"""
        try:
            import sys
            total_size = sys.getsizeof(self.cache)
            for key, entry in self.cache.items():
                total_size += sys.getsizeof(key)
                total_size += sys.getsizeof(entry)
                total_size += sys.getsizeof(entry['value'])
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0

# Global cache instance
cache = CacheManager()

def cached(ttl: int = 300, key_prefix: str = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        prefix = key_prefix or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache management methods to function
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: cache.get_stats()
        
        return wrapper
    return decorator

def cache_key(*args, **kwargs) -> str:
    """Generate a cache key from arguments"""
    return cache._generate_key("manual", *args, **kwargs)

# Specific cache decorators for common operations
def cache_user_data(ttl: int = 600):  # 10 minutes
    """Cache user data operations"""
    return cached(ttl=ttl, key_prefix="user_data")

def cache_food_data(ttl: int = 1800):  # 30 minutes
    """Cache food data operations"""
    return cached(ttl=ttl, key_prefix="food_data")

def cache_meal_plans(ttl: int = 900):  # 15 minutes
    """Cache meal plan operations"""
    return cached(ttl=ttl, key_prefix="meal_plans")

def cache_system_stats(ttl: int = 120):  # 2 minutes
    """Cache system statistics"""
    return cached(ttl=ttl, key_prefix="system_stats")

# Cache warming functions
def warm_cache():
    """Pre-populate cache with frequently accessed data"""
    logger.info("Starting cache warming...")
    
    try:
        # Import here to avoid circular imports
        from services.firestore_service import firestore_service
        
        # Warm up user data cache
        logger.info("Warming user data cache...")
        users = firestore_service.get_all_users()
        cache.set("warm:all_users", users, ttl=600)
        
        # Warm up food data cache
        logger.info("Warming food data cache...")
        foods = firestore_service.get_all_foods()
        cache.set("warm:all_foods", foods, ttl=1800)
        
        logger.info("Cache warming completed")
        
    except Exception as e:
        logger.error(f"Cache warming failed: {e}")

# Background task to cleanup expired entries
def schedule_cache_cleanup():
    """Schedule periodic cache cleanup"""
    import threading
    import time
    
    def cleanup_task():
        while True:
            time.sleep(300)  # Run every 5 minutes
            cache.cleanup_expired()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    logger.info("Cache cleanup scheduler started")
