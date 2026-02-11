"""
TrustLink Cache Manager
Implements multi-tier caching with Redis and in-memory fallback
Supports distributed caching for horizontal scaling
"""
import os
import json
import hashlib
import pickle
from datetime import timedelta
from functools import wraps
import time

# Try to import Redis, fall back to in-memory cache
try:
    import redis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheManager:
    """Multi-tier cache manager with Redis and in-memory fallback"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
        
        # Initialize Redis if available
        if REDIS_AVAILABLE:
            self._init_redis()
        
        print(f"[Cache] Initialized with Redis: {self.redis_enabled}")
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.redis_client.ping()
            print(f"[Cache] Connected to Redis: {redis_url}")
        except (RedisError, Exception) as e:
            print(f"[Cache] Redis connection failed: {e}. Using memory cache.")
            self.redis_client = None
    
    @property
    def redis_enabled(self):
        """Check if Redis is available and connected"""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    def _generate_key(self, key, namespace='trustlink'):
        """Generate cache key with namespace"""
        return f"{namespace}:{key}"
    
    def get(self, key, namespace='trustlink'):
        """Get value from cache (Redis or memory)"""
        cache_key = self._generate_key(key, namespace)
        
        # Try Redis first
        if self.redis_enabled:
            try:
                value = self.redis_client.get(cache_key)
                if value is not None:
                    self.cache_stats['hits'] += 1
                    try:
                        return json.loads(value)
                    except:
                        return value
                self.cache_stats['misses'] += 1
                return None
            except RedisError as e:
                self.cache_stats['errors'] += 1
                print(f"[Cache] Redis error on get: {e}")
        
        # Fall back to memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if entry['expires'] == 0 or entry['expires'] > time.time():
                self.cache_stats['hits'] += 1
                return entry['value']
            else:
                del self.memory_cache[cache_key]
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key, value, ttl=3600, namespace='trustlink'):
        """Set value in cache with TTL (Time To Live in seconds)"""
        cache_key = self._generate_key(key, namespace)
        
        # Try Redis first
        if self.redis_enabled:
            try:
                serialized = json.dumps(value) if not isinstance(value, str) else value
                self.redis_client.setex(cache_key, ttl, serialized)
                return True
            except (RedisError, TypeError) as e:
                self.cache_stats['errors'] += 1
                print(f"[Cache] Redis error on set: {e}")
        
        # Fall back to memory cache
        self.memory_cache[cache_key] = {
            'value': value,
            'expires': time.time() + ttl if ttl > 0 else 0
        }
        return True
    
    def delete(self, key, namespace='trustlink'):
        """Delete key from cache"""
        cache_key = self._generate_key(key, namespace)
        
        # Delete from Redis
        if self.redis_enabled:
            try:
                self.redis_client.delete(cache_key)
            except RedisError as e:
                print(f"[Cache] Redis error on delete: {e}")
        
        # Delete from memory cache
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        return True
    
    def clear(self, namespace='trustlink'):
        """Clear all keys in namespace"""
        # Clear Redis
        if self.redis_enabled:
            try:
                pattern = f"{namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except RedisError as e:
                print(f"[Cache] Redis error on clear: {e}")
        
        # Clear memory cache
        keys_to_delete = [k for k in self.memory_cache.keys() if k.startswith(f"{namespace}:")]
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        return True
    
    def increment(self, key, amount=1, namespace='trustlink'):
        """Increment a counter (atomic operation)"""
        cache_key = self._generate_key(key, namespace)
        
        # Use Redis for atomic increment
        if self.redis_enabled:
            try:
                return self.redis_client.incr(cache_key, amount)
            except RedisError as e:
                print(f"[Cache] Redis error on increment: {e}")
        
        # Fall back to memory (not atomic)
        if cache_key not in self.memory_cache:
            self.memory_cache[cache_key] = {'value': 0, 'expires': 0}
        
        self.memory_cache[cache_key]['value'] += amount
        return self.memory_cache[cache_key]['value']
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        stats = {
            'enabled': True,
            'backend': 'redis' if self.redis_enabled else 'memory',
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'errors': self.cache_stats['errors'],
            'total_requests': total_requests,
            'hit_rate': round(hit_rate, 2)
        }
        
        # Add Redis-specific stats
        if self.redis_enabled:
            try:
                info = self.redis_client.info('memory')
                stats['redis_memory'] = info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = self.redis_client.dbsize()
            except:
                pass
        else:
            stats['memory_keys'] = len(self.memory_cache)
        
        return stats
    
    def healthcheck(self):
        """Check cache health"""
        if self.redis_enabled:
            try:
                self.redis_client.ping()
                return True, "Redis connected"
            except:
                return False, "Redis unavailable"
        else:
            return True, "Memory cache active"


# Global cache instance
cache = CacheManager()


def cached(ttl=3600, namespace='trustlink', key_prefix=''):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
        namespace: Cache namespace
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix or func.__name__]
            
            # Add args to key
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))
            
            # Add kwargs to key
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}={v}")
            
            cache_key = ':'.join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key, namespace)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl, namespace)
            
            return result
        
        return wrapper
    return decorator


class DistributedRateLimiter:
    """Distributed rate limiter using Redis for horizontal scaling"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    def is_allowed(self, key, limit, window=3600):
        """
        Check if request is within rate limit
        
        Args:
            key: Unique identifier (user_id, ip_address, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds (default 1 hour)
        
        Returns:
            bool: True if allowed, False if rate limited
        """
        cache_key = f"ratelimit:{key}"
        
        # Use Redis for distributed rate limiting
        if self.cache.redis_enabled:
            try:
                current = self.cache.redis_client.get(cache_key)
                current = int(current) if current else 0
                
                if current >= limit:
                    return False
                
                # Increment counter
                pipe = self.cache.redis_client.pipeline()
                pipe.incr(cache_key)
                if current == 0:
                    pipe.expire(cache_key, window)
                pipe.execute()
                
                return True
            except Exception as e:
                print(f"[RateLimit] Error: {e}")
                # Fail open for availability
                return True
        
        # Fall back to memory-based rate limiting
        current = self.cache.get(cache_key, namespace='ratelimit') or 0
        
        if current >= limit:
            return False
        
        self.cache.set(cache_key, current + 1, window, namespace='ratelimit')
        return True
    
    def get_remaining(self, key, limit, window=3600):
        """Get remaining requests in current window"""
        cache_key = f"ratelimit:{key}"
        
        if self.cache.redis_enabled:
            try:
                current = self.cache.redis_client.get(cache_key)
                current = int(current) if current else 0
                return max(0, limit - current)
            except:
                return limit
        
        current = self.cache.get(cache_key, namespace='ratelimit') or 0
        return max(0, limit - current)
    
    def reset(self, key):
        """Reset rate limit for key"""
        cache_key = f"ratelimit:{key}"
        self.cache.delete(cache_key, namespace='ratelimit')


class SessionStore:
    """Distributed session store using Redis"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.namespace = 'session'
    
    def get(self, session_id):
        """Get session data"""
        return self.cache.get(session_id, self.namespace)
    
    def set(self, session_id, data, ttl=86400):
        """Set session data (default 24 hours)"""
        return self.cache.set(session_id, data, ttl, self.namespace)
    
    def delete(self, session_id):
        """Delete session"""
        return self.cache.delete(session_id, self.namespace)
    
    def extend(self, session_id, ttl=86400):
        """Extend session TTL"""
        data = self.get(session_id)
        if data:
            return self.set(session_id, data, ttl)
        return False


# Global instances
rate_limiter = DistributedRateLimiter(cache)
session_store = SessionStore(cache)
