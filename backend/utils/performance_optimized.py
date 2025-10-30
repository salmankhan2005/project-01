import time
import logging
import asyncio
from functools import wraps, lru_cache
from typing import Callable, Any, Dict, Optional, List
from datetime import datetime, timedelta
import threading
from concurrent.futures import ThreadPoolExecutor
import redis
import json
import hashlib

logger = logging.getLogger(__name__)

# Thread pool for async operations
executor = ThreadPoolExecutor(max_workers=4)

# Redis client for caching (with fallback to in-memory)
try:
    import os
    redis_url = os.getenv('REDIS_URL')
    if redis_url:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        redis_client.ping()  # Test connection
        logger.info("Redis cache initialized successfully")
    else:
        redis_client = None
        logger.info("Redis URL not provided, using in-memory cache")
except Exception as e:
    logger.warning(f"Redis connection failed, falling back to in-memory cache: {e}")
    redis_client = None

# In-memory cache fallback
memory_cache: Dict[str, Dict[str, Any]] = {}
cache_lock = threading.RLock()

class CacheManager:
    """Unified cache manager with Redis and in-memory fallback"""
    
    @staticmethod
    def _generate_key(prefix: str, *args, **kwargs) -> str:
        """Generate a consistent cache key"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if redis_client:
                value = redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                with cache_lock:
                    if key in memory_cache:
                        cache_entry = memory_cache[key]
                        if cache_entry['expires'] > datetime.now():
                            return cache_entry['value']
                        else:
                            del memory_cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache"""
        try:
            if redis_client:
                redis_client.setex(key, ttl, json.dumps(value, default=str))
            else:
                with cache_lock:
                    memory_cache[key] = {
                        'value': value,
                        'expires': datetime.now() + timedelta(seconds=ttl)
                    }
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """Delete value from cache"""
        try:
            if redis_client:
                redis_client.delete(key)
            else:
                with cache_lock:
                    memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    def clear_pattern(pattern: str) -> bool:
        """Clear cache entries matching pattern"""
        try:
            if redis_client:
                keys = redis_client.keys(pattern)
                if keys:
                    redis_client.delete(*keys)
            else:
                with cache_lock:
                    keys_to_delete = [k for k in memory_cache.keys() if pattern in k]
                    for key in keys_to_delete:
                        del memory_cache[key]
            return True
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return False

def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Enhanced caching decorator with better key generation"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = CacheManager._generate_key(
                f"{key_prefix}:{func.__name__}", *args, **kwargs
            )
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            CacheManager.set(cache_key, result, ttl)
            
            logger.debug(f"Cache miss for {func.__name__}, executed in {execution_time:.3f}s")
            return result
        return wrapper
    return decorator

def measure_performance(log_slow_queries: bool = True, slow_threshold: float = 1.0):
    """Enhanced performance measurement decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            start_memory = None
            
            try:
                import psutil
                process = psutil.Process()
                start_memory = process.memory_info().rss
            except ImportError:
                pass
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log performance metrics
                if log_slow_queries and execution_time > slow_threshold:
                    memory_used = ""
                    if start_memory:
                        try:
                            end_memory = psutil.Process().memory_info().rss
                            memory_diff = (end_memory - start_memory) / 1024 / 1024  # MB
                            memory_used = f", memory: +{memory_diff:.2f}MB"
                        except:
                            pass
                    
                    logger.warning(
                        f"Slow operation: {func.__name__} took {execution_time:.3f}s{memory_used}"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"Error in {func.__name__} after {execution_time:.3f}s: {e}")
                raise
                
        return wrapper
    return decorator

class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def optimize_supabase_query(query_builder, limit: int = 100, order_by: str = 'created_at'):
        """Optimize Supabase queries with proper limits and ordering"""
        return query_builder.limit(min(limit, 1000)).order(order_by, desc=True)
    
    @staticmethod
    def get_pagination_params(request, max_per_page: int = 100) -> tuple[int, int, int]:
        """Extract and validate pagination parameters"""
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = min(max_per_page, max(1, int(request.args.get('per_page', 20))))
            offset = (page - 1) * per_page
            return page, per_page, offset
        except (ValueError, TypeError):
            return 1, 20, 0
    
    @staticmethod
    def batch_process(items: List[Any], batch_size: int = 100):
        """Process items in batches for better performance"""
        if not items:
            return
        
        batch_size = max(1, min(batch_size, 1000))  # Limit batch size
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

class RateLimiter:
    """Simple rate limiting implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
        self.lock = threading.RLock()
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier"""
        current_time = time.time()
        
        with self.lock:
            if identifier not in self.requests:
                self.requests[identifier] = []
            
            # Remove old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < self.window_seconds
            ]
            
            # Check if limit exceeded
            if len(self.requests[identifier]) >= self.max_requests:
                return False
            
            # Add current request
            self.requests[identifier].append(current_time)
            return True
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests for identifier"""
        current_time = time.time()
        
        with self.lock:
            if identifier not in self.requests:
                return self.max_requests
            
            # Remove old requests
            self.requests[identifier] = [
                req_time for req_time in self.requests[identifier]
                if current_time - req_time < self.window_seconds
            ]
            
            return max(0, self.max_requests - len(self.requests[identifier]))

# Global rate limiter instance
rate_limiter = RateLimiter()

def async_task(func: Callable) -> Callable:
    """Decorator to run function asynchronously"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        future = executor.submit(func, *args, **kwargs)
        return future
    return wrapper

@lru_cache(maxsize=1000)
def cached_computation(data: str) -> str:
    """Example of using LRU cache for expensive computations"""
    # This is just an example - replace with actual computation
    return hashlib.md5(data.encode()).hexdigest()

def cleanup_cache():
    """Cleanup expired cache entries (for in-memory cache)"""
    if not redis_client:
        current_time = datetime.now()
        with cache_lock:
            expired_keys = [
                key for key, entry in memory_cache.items()
                if entry['expires'] <= current_time
            ]
            for key in expired_keys:
                del memory_cache[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Schedule cache cleanup every 5 minutes
def schedule_cache_cleanup():
    """Schedule periodic cache cleanup"""
    def cleanup_worker():
        while True:
            time.sleep(300)  # 5 minutes
            try:
                cleanup_cache()
            except Exception as e:
                logger.error(f"Cache cleanup error: {e}")
    
    cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
    cleanup_thread.start()

# Start cache cleanup scheduler
schedule_cache_cleanup()

# Performance monitoring
class PerformanceMonitor:
    """Monitor application performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'total_response_time': 0,
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.lock = threading.RLock()
    
    def record_request(self, response_time: float, error: bool = False):
        """Record request metrics"""
        with self.lock:
            self.metrics['request_count'] += 1
            self.metrics['total_response_time'] += response_time
            if error:
                self.metrics['error_count'] += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        with self.lock:
            self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        with self.lock:
            self.metrics['cache_misses'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            if self.metrics['request_count'] > 0:
                avg_response_time = self.metrics['total_response_time'] / self.metrics['request_count']
                error_rate = self.metrics['error_count'] / self.metrics['request_count']
            else:
                avg_response_time = 0
                error_rate = 0
            
            total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
            cache_hit_rate = (self.metrics['cache_hits'] / total_cache_requests) if total_cache_requests > 0 else 0
            
            return {
                'request_count': self.metrics['request_count'],
                'avg_response_time': round(avg_response_time, 3),
                'error_rate': round(error_rate, 3),
                'cache_hit_rate': round(cache_hit_rate, 3),
                'total_errors': self.metrics['error_count']
            }

# Global performance monitor
performance_monitor = PerformanceMonitor()